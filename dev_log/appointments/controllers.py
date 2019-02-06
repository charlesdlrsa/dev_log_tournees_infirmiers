from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from sqlalchemy.sql import or_
import datetime
from dev_log.utils import calendar
from dev_log import db
from dev_log.models import Appointment, Patient, Nurse, Care, Office
from dev_log.auth.controllers import admin_required

# from dev_log.opti.space import solve_boolean


appointments = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointments.route('/', methods=['GET', 'POST'])
@admin_required
def home():
    if request.method == "POST":
        if request.form.get('input_patient') is not None:
            patient_id = request.form['input_patient']
            date = request.form['date']
            date_selected = calendar.get_dates_from_form(date)[0]
            care_id = request.form['input_care']
            error = None

            if patient_id == "":
                error = "You need to select a nurse to view a planning"
            elif care_id == "":
                error = "You need to select a care"
            elif date_selected <= datetime.date.today() + datetime.timedelta(1):
                error = "You cannot add an appointment less than 24 hours before the desired date."
            if error is not None:
                flash(error)
            else:
                return redirect(url_for('appointments.availabilities', patient_id=patient_id, date=date,
                                        care_id=care_id))
        elif request.form.get('patient_appointments_research') is not None:
            research = request.form['patient_appointments_research']
            return redirect(url_for('appointments.search_patient_appointments', research=research))
        else:
            error = 'You must choose a patient.'
            flash(error)

    patients = Patient.query.filter(Patient.office_id == session['office_id']).order_by(Patient.last_name)
    cares = Care.query.all()

    return render_template("appointments_home.html", patients=patients, cares=cares)


@appointments.route('/availabilities/patient-<int:patient_id>/date-<date>/care-<care_id>', methods=['GET', 'POST'])
@admin_required
def availabilities(patient_id, date, care_id):
    if request.method == "POST":
        patient_id = request.form['input_patient']
        date = request.form['date']
        date_selected = calendar.get_dates_from_form(date)[0]
        care_id = request.form['input_care']

        if date_selected <= datetime.date.today():
            error = "You cannot add an appointment 24 hours before the wanted date."
            flash(error)
        else:
            return redirect(url_for('appointments.availabilities', patient_id=patient_id, date=date, care_id=care_id))

    date_selected, date_start_week, date_end_week = calendar.get_dates_from_form(date)

    availabilities = [{} for _ in range(7)]
    for week_day in range(7):
        date = date_start_week + datetime.timedelta(week_day)
        availabilities[week_day]['date'] = date
        for halfday in ['Morning', 'Afternoon']:
            appointment = check_appointments_patient(patient_id, date, halfday=halfday)
            if appointment is None:
                if check_appointments_nurses(care_id, date, halfday=halfday) is True:
                    availabilities[week_day][halfday] = "A nurse is available"
                else:
                    availabilities[week_day][halfday] = "No nurse is available"
            else:
                availabilities[week_day][halfday] = "Appointment already scheduled: -- {} --".format(appointment)

    patient = Patient.query.get(patient_id)
    care = Care.query.get(care_id)

    return render_template("availabilities.html", availabilities=availabilities, date_selected=date_selected,
                           date_start_week=date_start_week, date_end_week=date_end_week, patient=patient,
                           care=care)


@appointments.route('/research-<research>', methods=['GET', 'POST'])
def search_patient_appointments(research):
    if request.method == "POST":
        research = request.form['patient_appointments_research']
        return redirect(url_for('appointments.search_patient_appointments', research=research))

    if len(research.split()) >= 2:
        first_name, last_name = research.split()[0], " ".join(research.split()[1:])
        appointments = Appointment.query \
            .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + last_name + '%'),
                                                  Patient.first_name.like('%' + first_name + '%')))
    else:
        appointments = Appointment.query \
            .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + research + '%'),
                                                  Patient.first_name.like('%' + research + '%')))

    return render_template('appointments.html', appointments=appointments)


def check_appointments_nurses(care_id, date, halfday):
    # nurses = Nurse.query.filter(Nurse.office_id == session['office_id'])
    # office = Office.query.filter(Office.id == session['office_id'])
    # data = {}
    # data["nurse_ids"] = [str(nurse.id) for nurse in nurses]
    # data["office_lat"] = str(office[0].latitude)
    # data["office_lon"] = str(office[0].longitude)
    # if halfday == "Morning":
    #     data["start"] = "08:00"
    #     data["end"] = "12:30"
    # if halfday == "Afternoon":
    #     data["start"] = "13:30"
    #     data["end"] = "18:00"
    #
    # appointments = Appointment.query.filter(Appointment.date == date, Appointment.halfday == halfday).all()
    # data["appointments"] = []
    # for app in appointments:
    #     patient = Patient.query.filter(Patient.id == app.patient_id).all()
    #     care = Care.query.filter(Care.id == app.care_id).all()
    #     app_data = {}
    #     app_data["app_id"] = str(app.id)
    #     app_data["app_lat"] = str(patient[0].latitude)
    #     app_data["app_lon"] = str(patient[0].longitude)
    #     app_data["app_length"] = str(care[0].duration)
    #     data["appointments"].append(app_data)
    # response = solve_boolean(data)
    response = True
    return response


def check_appointments_patient(patient_id, date, halfday):
    """Checks existing appointment on this halfday for this patient and returns associated care"""

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
    """
    Add a new appointment in database.
    """
    date_selected = calendar.get_dates_from_form(date)[0]
    appointment = Appointment(patient_id=patient_id, date=date_selected, care_id=care_id, halfday=halfday)
    db.session.add(appointment)
    db.session.commit()
    flash('The appointment was successfully added on {} in the morning'.format(date_selected.strftime("%d/%m/%y")))
    return redirect(url_for('appointments.home'))


@appointments.route('/delete_appointment/<int:appointment_id>')
@admin_required
def delete_appointment(appointment_id):
    """
    Delete an appointment with its id from the database.
    """
    appointment = Appointment.query.get(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash("The appointment was successfully deleted.")
    return redirect(url_for('appointments.home'))
