from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from sqlalchemy.sql import or_
from datetime import datetime
from dev_log import db
from dev_log.models import Appointment, Patient

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

        return redirect(url_for(get_appointments, research=research))

    appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments)


@appointments.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    """
    Add a new appointment
    :return:
    """
    if request.method == 'POST':
        nurse_id = request.form['nurse_id']
        patient_id = request.form['patient_id']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        print('le type:')
        print(type(date))
        care = request.form['care']
        error = None

        if not nurse_id:
            error = 'A nurse is required.'
        elif not patient_id:
            error = 'A patient is required.'
        elif not date:
            error = 'Date is required.'
        elif not care:
            error = 'Care is required.'

        else:
            # storing the new appointment information in the db
            print('here')
            appointment = Appointment(nurse_id, patient_id, date, care)
            print('there we are')
            print(appointment.patient_name)
            db.session.add(appointment)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('appointments.home'))

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
