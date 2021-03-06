from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from sqlalchemy.sql import or_
import datetime
from dev_log.utils import calendar
from dev_log import db
from dev_log.models import Appointment, Patient, Nurse, Care, Office, Schedule
from dev_log.auth.controllers import admin_required
from dev_log.optim.space import solve_boolean, GmapApiError
from dev_log.utils.optimizer_functions import build_data_for_optimizer

appointments = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointments.route('/', methods=['GET', 'POST'])
@admin_required
def home():
    """ Appointments'home page allowing to set a new appointment for a patient
    or to view the appointments already taken for a patient """

    if request.method == "POST":
        if request.form.get('input_patient') is not None:
            patient_id = request.form['input_patient']
            date = request.form['date']
            date_selected = calendar.get_dates_from_form(date)[0]
            # Function available in the module "calendar" in devlog.utils
            # It returns, in date format, the date of the selected day.
            care_id = request.form['input_care']
            error = None

            if patient_id == "":
                error = "You need to select a nurse to view a planning"
            elif care_id == "":
                error = "You need to select a care"
            elif date_selected <= datetime.date.today() + datetime.timedelta(1):
                error = "You cannot add an appointment less than 24 hours before the desired date."
                # To be able to set the nurses' planning 24 hours before each day, we forbidden the admin to add
                # appointments after this delay. See planning's controllers for more explications.
            if error is not None:
                flash(error)
            else:
                return redirect(url_for('appointments.availabilities', patient_id=patient_id, date=date,
                                        care_id=care_id))
        elif request.form['date_appointments_research'] != "" or request.form['patient_appointments_research'] != "":
            date_research = request.form['date_appointments_research']
            if date_research == "":
                date_research = "all"
            patient_research = request.form['patient_appointments_research']
            if patient_research == "":
                patient_research = "all"
            # we call the function "search_patient_appointments"
            return redirect(
                url_for('appointments.search_patient_appointments', patient=patient_research, date=date_research))
        else:
            error = 'You must choose a patient or a date.'
            flash(error)

    patients = Patient.query.filter(Patient.office_id == session['office_id']).order_by(Patient.last_name)
    cares = Care.query.all()

    return render_template("appointments_home.html", patients=patients, cares=cares)


@appointments.route('/availabilities/patient-<int:patient_id>/date-<date>/care-<care_id>', methods=['GET', 'POST'])
@admin_required
def availabilities(patient_id, date, care_id):
    """ Function returning the nurses'availabilities for all the half-days of the week of the day selected """

    if request.method == "POST":
        patient_id = request.form['input_patient']
        date = request.form['date']
        date_selected = calendar.get_dates_from_form(date)[0]
        care_id = request.form['input_care']

        if date_selected <= datetime.date.today():
            error = "You cannot add an appointment 24 hours before the desired date."
            # To be able to set the nurses' planning 24 hours before each day, we forbidden the admin to add
            # appointments after this delay. See planning's controllers for more explications.
            flash(error)
        else:
            return redirect(url_for('appointments.availabilities', patient_id=patient_id, date=date, care_id=care_id))

    date_selected, date_start_week, date_end_week = calendar.get_dates_from_form(date)
    # Function available in the module "calendar" in devlog.utils
    # It returns, in date format, the dates of the selected day, the first day and the last day
    # of the week of the selected day

    availabilities = [{} for _ in range(7)]
    for week_day in range(7):
        date = date_start_week + datetime.timedelta(week_day)
        availabilities[week_day]['date'] = date
        for halfday in ['Morning', 'Afternoon']:
            # for each half-day of the week, we check if a nurse is available and if the patient doesn't already have
            # an appointment by calling the functions : check_appointments_patient and check_appointments_nurses
            if date <= datetime.date.today() + datetime.timedelta(1) or \
                    (date == datetime.date(2019, 5, 2) and halfday == "Morning"):
                # impossible to book an appointment less than 24 hours before the desired date
                availabilities[week_day][halfday] = "Closed appointment booking"
            else:
                appointment = check_appointments_patient(patient_id, date, halfday=halfday)
                if appointment is None:
                    try:
                        if check_appointments_nurses(care_id, patient_id, date, halfday=halfday) is True:
                            availabilities[week_day][halfday] = "A nurse is available"
                        else:
                            availabilities[week_day][halfday] = "No nurse is available"
                    except GmapApiError:
                        error = "You need to be connected to see the availabilities. " \
                                "Please check your network connexion and try again."
                        flash(error)
                        return redirect(url_for('appointments.home'))
                else:
                    availabilities[week_day][halfday] = "Appointment already scheduled: '{}' ".format(appointment)

    patient = Patient.query.get(patient_id)
    care = Care.query.get(care_id)

    return render_template("availabilities.html", availabilities=availabilities, date_selected=date_selected,
                           date_start_week=date_start_week, date_end_week=date_end_week, patient=patient,
                           care=care)


@appointments.route('/research/date-<date>/patient-<patient>', methods=['GET', 'POST'])
def search_patient_appointments(date, patient):
    """ Function allowing to search the patient's appointments """

    if request.method == "POST":
        if request.form['date_appointments_research'] != "" or request.form['patient_appointments_research'] != "":
            date_research = request.form['date_appointments_research']
            if date_research == "":
                date_research = "all"
            patient_research = request.form['patient_appointments_research']
            if patient_research == "":
                patient_research = "all"
            # we call the function "search_patient_appointments"
            return redirect(
                url_for('appointments.search_patient_appointments', patient=patient_research, date=date_research))
        else:
            error = 'You must choose a patient or a date.'
            flash(error)

    if patient == "all":
        date_selected = calendar.get_dates_from_form(date)[0]
        appointments = Appointment.query.filter(Appointment.date == date_selected)
    elif date == "all":
        if len(patient.split()) >= 2:
            first_name, last_name = patient.split()[0], " ".join(patient.split()[1:])
            appointments = Appointment.query \
                .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + last_name + '%'),
                                                      Patient.first_name.like('%' + first_name + '%'))).order_by(
                Appointment.date)
        else:
            appointments = Appointment.query \
                .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + patient + '%'),
                                                      Patient.first_name.like('%' + patient + '%'))).order_by(
                Appointment.date)
    else:
        date_selected = calendar.get_dates_from_form(date)[0]
        if len(patient.split()) >= 2:
            first_name, last_name = patient.split()[0], " ".join(patient.split()[1:])
            appointments = Appointment.query \
                .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + last_name + '%'),
                                                      Patient.first_name.like('%' + first_name + '%')),
                                                  Appointment.date == date_selected)
        else:
            appointments = Appointment.query \
                .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + patient + '%'),
                                                      Patient.first_name.like('%' + patient + '%')),
                                                  Appointment.date == date_selected)

    return render_template('appointments.html', appointments=appointments)


def check_appointments_nurses(care_id, patient_id, date, halfday):
    """ Function checking if the nurses are able to do all the appointments of the selected half-day, plus the new
    appointment that the administrator wants to schedule by calling the optimizer function """

    appointments_and_available_nurses_for_this_date = build_data_for_optimizer(date, halfday, care_id,
                                                                               patient_id=patient_id)
    print(appointments_and_available_nurses_for_this_date)
    response = solve_boolean(appointments_and_available_nurses_for_this_date)

    return response


def check_appointments_patient(patient_id, date, halfday):
    """ Function checking the existing appointments on a specific half-day for a patient
    and returns associated care """

    appointment = Appointment.query.filter(Appointment.date == date,
                                           Appointment.halfday == halfday,
                                           Appointment.patient_id == patient_id).first()
    if appointment is None:
        return None

    else:
        care_description = appointment.care.description
        return care_description


@appointments.route('/add_appointment/patient-<int:patient_id>/date-<date>/care-<care_id>/halfday-<halfday>',
                    methods=['GET', 'POST'])
def add_appointment(patient_id, date, care_id, halfday):
    """ Add a new appointment defined by its patient, care and date in the database """

    date_selected = calendar.get_dates_from_form(date)[0]
    appointment = Appointment(patient_id=patient_id, date=date_selected, care_id=care_id, halfday=halfday)
    db.session.add(appointment)
    db.session.commit()
    flash('The appointment was successfully added on {} in the {}'.format(date_selected.strftime("%d/%m/%y"), halfday))
    return redirect(url_for('appointments.home'))


@appointments.route('/delete_appointment/<int:appointment_id>')
@admin_required
def delete_appointment(appointment_id):
    """ Delete an appointment with its id from the database """

    appointment = Appointment.query.get(appointment_id)
    schedule = Schedule.query.filter(Schedule.appointment_id == appointment_id).first()
    db.session.delete(appointment)
    try:
        db.session.delete(schedule)
    except:
        pass
    db.session.commit()
    flash("The appointment was successfully deleted.")
    return redirect(url_for('appointments.home'))
