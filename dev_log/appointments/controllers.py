from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from sqlalchemy.sql import or_
from datetime import datetime
from dev_log import db
from dev_log.models import Appointment, Patient, Nurse
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
            return redirect(url_for('appointments.get_appointments', research=research))

    appointments = db.session.query(Appointment).order_by(Appointment.date).all()
    return render_template("appointments.html", appointments=appointments)


@appointments.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    """
    Add a new appointment
    :return:
    """
    if request.method == 'POST':
        patient = request.form['patient'].split(' - ')
        nurse = request.form['nurse'].split(' - ')
        patient_id = db.session.query(Patient).filter(Patient.first_name == patient[1]).filter(
            Patient.last_name == patient[0]).first().id

        # en principe à enlever car l'attribution se fait avec l'optimiseur
        nurse_id = db.session.query(Nurse).filter(Nurse.first_name == nurse[1]).filter(
            Nurse.last_name == nurse[0]).first().id

        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        care = request.form['care']
        error = None

        if not patient:
            error = 'Please select a patient.'
        elif not date:
            error = 'A date is required.'
        elif date < date.today():
            error = 'You selected a day already passed.'
        elif not care:
            error = 'A care is required.'
        elif Appointment.query.filter(Appointment.date == date).count() == db.session.query(Nurse).count() * 3:
            error = 'You cannot add an appointment on %s, all the nurses are already affected.' \
                    '\n You must choose another date. Please look at the calendar to see the available slots.'.format(
                date)
        else:
            # storing the new appointment information in the db
            appointment = Appointment(nurse_id, patient_id, date, care)
            db.session.add(appointment)
            db.session.commit()
            flash('The appointment was successfully added')
            return redirect(url_for('appointments.home'))
        flash(error)

    patients = db.session.query(Patient).order_by(Patient.last_name).all()
    nurses = db.session.query(Nurse).order_by(Nurse.last_name).all()

    return render_template('add_appointment.html', patients=patients, nurses=nurses)


@appointments.route('/get_appointments/<research>', methods=['GET', 'POST'])
def get_appointments(research):
    if request.method == "POST":
        error = None
        new_research = request.form['research']
        return redirect(url_for('appointments.get_appointments', research=new_research))

    if len(research.split()) == 2:
        first_name, last_name = research.split()
        appointments = Appointment.query \
            .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + last_name + '%'),
                                                  Patient.first_name.like('%' + first_name + '%')))
    else:
        appointments = Appointment.query \
            .join(Appointment.patient).filter(or_(Patient.last_name.like('%' + research + '%'),
                                                  Patient.first_name.like('%' + research + '%')))

    return render_template('appointments.html', appointments=appointments)
