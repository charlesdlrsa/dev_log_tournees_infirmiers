from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from sqlalchemy.sql import or_
import datetime
from dev_log.utils import calendar
from dev_log import db
from dev_log.models import Appointment, Patient, Nurse, Care, Office
from dev_log.auth.controllers import login_required
from dev_log.auth.controllers import admin_required

# from dev_log.opti.space import solve_boolean


appointments = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointments.route('/', methods=['GET', 'POST'])
@admin_required
def home():
    if request.method == "POST":
        patient_id = request.form['input_patient']
        date = request.form['date']
        date_selected = calendar.get_dates_from_form(date)[0]
        care_id = request.form['input_care']
        error = None

        if patient_id == "":
            error = "You need to select a nurse to view a planning"
        elif care_id == "":
            error = "You need to select a care"
        elif date_selected <= datetime.date.today():
            error = "You cannot add an appointment 24 hours before the wanted date."
        if error is not None:
            flash(error)
        else:
            return redirect(url_for('appointments.availabilities', patient_id=patient_id, date=date,
                                    care_id=care_id))

    patients = Patient.query.filter(Patient.office_id == session['office_id'])
    cares = db.session.query(Care).all()

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
                availabilities[week_day][halfday] = "An appointment ({}) is already scheduled".format(appointment)

    patient = Patient.query.filter(Patient.id == patient_id).first()
    care = Care.query.filter(Care.id == care_id).first()

    return render_template("availabilities.html", availabilities=availabilities, date_selected=date_selected,
                           date_start_week=date_start_week, date_end_week=date_end_week, patient=patient,
                           care=care)


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
    #     patient = db.session.query(Patient).filter(Patient.id == app.patient_id).all()
    #     care = db.session.query(Care).filter(Care.id == app.care_id).all()
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


@appointments.route('/add_appointment/patient-<int:patient_id>/date-<date>/care-<care_id>/halfday-<halfday>', methods=['GET', 'POST'])
def add_appointment(patient_id, date, care_id, halfday):
    """
    Add a new appointment
    :return:
    """
    date_selected = calendar.get_dates_from_form(date)[0]
    appointment = Appointment(patient_id=patient_id, date=date_selected, care_id=care_id, halfday=halfday)
    db.session.add(appointment)
    db.session.commit()
    flash('The appointment was successfully added on {} in the morning'.format(date_selected.strftime("%d/%m/%y")))
    return redirect(url_for('appointments.home'))


