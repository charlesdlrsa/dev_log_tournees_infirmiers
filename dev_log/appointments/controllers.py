from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from sqlalchemy.sql import or_
from datetime import datetime, date
from dev_log.utils.calendar import *
from dev_log import db
from dev_log.models import Appointment, Patient, Nurse, Care
from datetime import *
from dev_log.auth.controllers import login_required
from dev_log.auth.controllers import admin_required


appointments = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointments.route('/', methods=['GET', 'POST'])
@admin_required
def home():
    if request.method == "POST":
        research = request.form['research']
        error = None
        if not research:
            error = 'Please enter the name of our patient.'
        if error is not None:
            flash(error)
        else:
            return redirect(url_for('appointments.search_appointments', research=research))
    appointments = dict()
    for i in range(1, 8):
        appointments[i] = []
    appointments_list = db.session.query(Appointment).order_by(Appointment.date).all()
    for appointment in appointments_list:
        appointments[appointment.date.weekday()].append(appointment)

    if "week" in request.args:
        week=int(request.args['week'])
        year=int(request.args['year'])
        if week==0:
            week=52
            year=year-1
        elif week==53:
            week=1
            year=year+1
    else:
        current_date = datetime.now()
        week = current_date.isocalendar()[1]
        year = current_date.isocalendar()[0]
    start_week = iso_to_gregorian(year, week, 1)
    end_week = iso_to_gregorian(year, week, 7)
    start_week = str(start_week.day) + '/' + str(start_week.month)
    end_week = str(end_week.day) + '/' + str(end_week.month)

    return render_template("appointments.html", appointments=appointments, start_week=start_week,
                           end_week=end_week, year=year, week=week)


@appointments.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    """
    Add a new appointment
    :return:
    """
    if "week" in request.args:
        day=int(request.args["day"])
        week=int(request.args["week"])
        year=int(request.args["year"])
        time=iso_to_gregorian(year,week,day)
        time = time.strftime('%Y-%m-%d')
    else:
        time=None
    if request.method == 'POST':
        patient = request.form['patient'].split(' - ')
        nurse = request.form['nurse'].split(' - ')
        patient_id = db.session.query(Patient).filter(Patient.first_name == patient[1]).filter(
            Patient.last_name == patient[0]).first().id

        # en principe à enlever car l'attribution se fait avec l'optimiseur
        nurse_id = db.session.query(Nurse).filter(Nurse.first_name == nurse[1]).filter(
            Nurse.last_name == nurse[0]).first().id

        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
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
            appointment = Appointment(nurse_id, patient_id, date, care, halfday)
            db.session.add(appointment)
            db.session.commit()
            flash('The appointment was successfully added')
            return redirect(url_for('appointments.home'))
        flash(error)

    patients = db.session.query(Patient).order_by(Patient.last_name).all()
    nurses = db.session.query(Nurse).order_by(Nurse.last_name).all()
    cares = db.session.query(Care).all()

    return render_template('add_appointment.html', patients=patients, nurses=nurses, cares=cares, time=time)


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

    return render_template('appointments.html', appointments=appointments)
