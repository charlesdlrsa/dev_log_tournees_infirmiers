from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from sqlalchemy.sql import or_
from datetime import datetime
from dev_log import db
from dev_log.models import Appointment, Patient, Nurse


appointments = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointments.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('get_appointments', research=research))

    appointments = Appointment.query.all()
    return render_template("appointments.html", appointments=appointments)


@appointments.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    """
    Add a new appointment
    :return:
    """
    if request.method == 'POST':
        # nurse_id = request.form['nurse_last_name']
        patient_id = request.form['patient_id']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        care = request.form['care']
        error = None

        if not nurse_id:
            error = 'Please select a nurse'
        elif not patient_id:
            error = 'Please select a patient.'
        elif not date:
            error = 'A date is required.'
        elif not care:
            error = 'A care is required.'
        elif Appointment.query.filter(Appointment.date == date).count() == Nurse.query.all().count()*3:
            error = 'You cannot add an appointment on %s, all the nurses are already affected.' \
                    '\n You must choose another date. Please look at the calendar to see the available slots.'.format(date)
        else:
            # storing the new appointment information in the db
            appointment = Appointment(None, patient_id, date, care)
            db.session.add(appointment)
            db.session.commit()
            flash('The appointment was successfully added')
            return redirect(url_for('get_appointments'))

        flash(error)

    return render_template('add_appointment.html')


@appointments.route('/get_appointments/<research>', methods=['GET', 'POST'])
def get_appointments(research):
    first_name, last_name = research.split()
    if request.method == "POST":
        error = None

    appointments = Appointment.query \
        .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + last_name + '%'),
                                              Patient.first_name.like('%' + first_name + '%')))
    return render_template('appointments.html', appointments=appointments)
