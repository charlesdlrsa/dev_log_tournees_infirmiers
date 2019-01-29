from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from sqlalchemy.sql import or_
from datetime import datetime
from dev_log.utils.calendar import *
from dev_log import db
from dev_log.models import Appointment, Patient, Nurse, Care, Office
from dev_log.auth.controllers import login_required
from dev_log.auth.controllers import admin_required

# from dev_log.opti.space import solve_boolean


appointments = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointments.route('/', methods=['GET', 'POST'])
@admin_required
def home():
    print(request.args)
    if request.method == "POST":
        error = False
        if "research" in request.form.keys():
            if request.form['research'] != "Choose Patient":
                research = request.form['research']
            else:
                research = None
                error = True
        else:
            research = None
        if "care_research" in request.form.keys():
            if request.form["care_research"] != "Choose Care":
                care_research = request.form["care_research"]
            else:
                care_research = None
                error=True
        else:
            care_research = None
        if "date" in request.form.keys():
            date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        else:
            date = None
            error = True
        if error:
            error_message = "Please correctly select a patient, a care and a date"
            flash(error_message)
        else:
            return redirect(url_for('appointments.home', research=research, care_research=care_research, date=date))


    day = 1
    if "date" in request.args:
        current_date = datetime.datetime.strptime(request.args['date'], '%Y-%m-%d').date()
    else:
        current_date = datetime.datetime.now()
    week = current_date.isocalendar()[1]
    year = current_date.isocalendar()[0]
    time = iso_to_gregorian(year, week, day)
    time = time.strftime('%Y-%m-%d')
#    print(request.args)
    if "research" in request.args:
        research = request.args["research"]
        patient = request.args["research"]
        patient = patient.split(' - ')
        appointments = [[] for k in range(7)]
        i = 1
        for day in appointments:
            date = iso_to_gregorian(year, week, i)
            day.append(check_appointments_patient(date=date, halfday="Morning", patient=patient))
            day.append(check_appointments_patient(date=date, halfday="Afternoon", patient=patient))
            #print(day)
            i += 1
    else:
        appointments = [[None, None] for k in range(7)]
        research = None

#    print(appointments)
    start_week = iso_to_gregorian(year, week, 1)
    end_week = iso_to_gregorian(year, week, 7)
    start_week = str(start_week.day) + '/' + str(start_week.month)
    end_week = str(end_week.day) + '/' + str(end_week.month)
    patients = db.session.query(Patient).order_by(Patient.last_name).all()
    nurses = db.session.query(Nurse).order_by(Nurse.last_name).all()

    if "care_research" in request.args:
        care_research = request.args["care_research"]
        care_id = db.session.query(Care).filter(Care.description == request.args["care_research"]).first().id
    else:
        care_id = 1
        care_research = None

    start_week = iso_to_gregorian(year, week, 1)
    end_week = iso_to_gregorian(year, week, 7)
    start_week = str(start_week.day) + '/' + str(start_week.month)
    end_week = str(end_week.day) + '/' + str(end_week.month)
    patients = db.session.query(Patient).order_by(Patient.last_name).all()
    nurses = db.session.query(Nurse).order_by(Nurse.last_name).all()
    cares = db.session.query(Care).order_by(Care.description).all()
    office = db.session.query(Office).all()

    if not ("care_research" in request.args and "research" in request.args and "date" in request.args):
        return render_template('appointments_home.html',start_week=start_week,end_week=end_week,year=year,week=week,patients=patients,
        nurses=nurses,cares=cares,time=time)

    availabilities = [[] for k in range(7)]
    i = 1
    for day in availabilities:
        date = iso_to_gregorian(year, week, i)
        day.append(check_availability(date=date, nurses=nurses, cares=cares,
                                      office=office, halfday="Morning"))
        day.append(check_availability(date=date, nurses=nurses, cares=cares,
                                      office=office, halfday="Afternoon"))
        # day.append(check_availability(date=date, halfday="Morning", care_id=care_id))
        # day.append(check_availability(date=date, halfday="Afternoon", care_id=care_id))
        i += 1


    return render_template("appointments.html", availabilities=availabilities, start_week=start_week,
                           end_week=end_week, year=year, week=week, patients=patients,
                           appointments=appointments, research=research, nurses=nurses,
                           cares=cares, care_research=care_research, time=time)


@appointments.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    """
    Add a new appointment
    :return:
    """
    if "research" in request.args:
        research = request.args["research"]
    else:
        research = None
    if "care_research" in request.args:
        care_research = request.args["care_research"]
    else:
        care_research = None
    if "week" in request.args:
        day = int(request.args["day"])
        week = int(request.args["week"])
        year = int(request.args["year"])
        halfday = request.args["halfday"]
        time = iso_to_gregorian(year, week, day)
        time = time.strftime('%Y-%m-%d')
    else:
        time = None
        halfday = None

    if request.method == 'POST':
        patient = request.form['patient'].split(' - ')
        patient_id = db.session.query(Patient).filter(Patient.first_name == patient[1]).filter(
            Patient.last_name == patient[0]).first().id
        date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        halfday = request.form['halfday']
        care = Care.query.filter(Care.description == request.form['care']).first().id
        error = None

        if not patient:
            error = 'Please select a patient.'
        elif not date:
            error = 'A date is required.'
        elif date < date.today():
            error = 'You selected a day already passed.'
        elif not care:
            error = 'A care is required.'
        elif not halfday:
            error = 'Please give a halfday'
        elif Appointment.query.filter(Appointment.date == date).count() == db.session.query(Nurse).count() * 3:
            error = 'You cannot add an appointment on %s, all the nurses are already affected.' \
                    '\n You must choose another date. Please look at the calendar to see the available slots.'.format(
                date)
        else:
            # storing the new appointment information in the db
            appointment = Appointment(patient_id, date, care, halfday)
            db.session.add(appointment)

            db.session.commit()
            flash('The appointment was successfully added')
            return redirect(url_for('appointments.home'))
        flash(error)

    patients = db.session.query(Patient).order_by(Patient.last_name).all()
    nurses = db.session.query(Nurse).order_by(Nurse.last_name).all()
    cares = db.session.query(Care).all()

    return render_template('add_appointment.html', patients=patients, nurses=nurses, cares=cares, time=time,
                           halfday=halfday, research=research, care_research=care_research)


@appointments.route('/get_appointments/<research>', methods=['GET', 'POST'])
def search_appointments(research):
    if request.method == "POST":
        error = None
        new_research = request.form['research']

        if not new_research:
            error = 'Please enter the name of a patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('appointment.search_appointment', research=new_research))

    if len(research.split()) >= 2:
        first_name, last_name = research.split()[0], " ".join(research.split()[1:])
        appointments = Appointment.query \
            .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + last_name + '%'),
                                                  Patient.first_name.like('%' + first_name + '%')))
    else:
        appointments = Appointment.query \
            .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + research + '%'),
                                                  Patient.first_name.like('%' + research + '%')))

    return redirect(url_for('appointment.home'))


# def check_availability(date, halfday, care_id):
#     nb_appointments = Appointment.query.filter(Appointment.date == date, Appointment.halfday == halfday).count()
#     nb_nurses = db.session.query(Nurse).count()
#
#     if nb_appointments >= nb_nurses * 4:
#         return False
#     else:
#         nb_specific_appointments = Appointment.query.filter(Appointment.date == date, Appointment.halfday == halfday,
#                                                             Appointment.care_id == care_id).count()
#         nb_specific_nurses = Nurse.query.filter(Nurse.cares.contains("-{}-".format(care_id))).count()
#
#         if nb_specific_appointments >= nb_specific_nurses * 4:
#             return False
#         else:
#             return True

def check_availability(date, nurses, cares, office, halfday):
    data = {}
    data["nurse_ids"] = [str(nurse.id) for nurse in nurses]
    data["office_lat"] = str(office[0].latitude)
    data["office_lon"] = str(office[0].longitude)
    if halfday == "Morning":
        data["start"] = "08:00"
        data["end"] = "12:30"
    if halfday == "Afternoon":
        data["start"] = "13:30"
        data["end"] = "18:00"

    appointments = Appointment.query.filter(Appointment.date == date, Appointment.halfday == halfday).all()
    data["appointments"] = []
    for app in appointments:
        patient = db.session.query(Patient).filter(Patient.id == app.patient_id).all()
        care = db.session.query(Care).filter(Care.id == app.care_id).all()
        app_data = {}
        app_data["app_id"] = str(app.id)
        app_data["app_lat"] = str(patient[0].latitude)
        app_data["app_lon"] = str(patient[0].longitude)
        app_data["app_length"] = str(care[0].duration)
        data["appointments"].append(app_data)
    # response = solve_boolean(data)
    response = True
    return response


def check_appointments_patient(date, halfday, patient):
    """Checks existing appointment on this halfday for this patient and returns associated care"""

    patient_id = db.session.query(Patient).filter(Patient.first_name == patient[1]).filter(
        Patient.last_name == patient[0]).first().id

    appointment = db.session.query(Appointment).filter(Appointment.date == date).filter(
        Appointment.halfday == halfday.lower()).filter(Appointment.patient_id == patient_id).first()

    try:
        id = appointment.care_id

        answer = db.session.query(Care).filter(Care.id == id).first().description

    except:
        answer = None

    return answer

# def check_appointments_nurse(date,halfday,nurse):
#     """Checks existing appointment on this halfday for this patient and returns associated care"""
#
#     nurse_id = db.session.query(Nurse).filter(Nurse.first_name == nurse[1]).filter(
#         Nurse.last_name == nurse[0]).first().id
#     appointment = db.session.query(Appointment).filter(Appointment.date == date).filter(
#     Appointment.halfday == halfday).filter(Appointment.nurse_id==nurse_id).first()
#     try:
#         id = appointment.care_id
#         answer = db.session.query(Care).filter(Care.id == id).first().description
#     except:
#         answer = None
#     return answer
