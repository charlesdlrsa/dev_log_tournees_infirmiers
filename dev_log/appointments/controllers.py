from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from dev_log import db
from dev_log.models import Appointment

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
            return redirect(url_for('get_appointments', patient_name=research))

        return redirect(url_for(get_appointments, last_name=last_name, first_name=first_name))

    appointments = Appointment.query.all()
    return render_template(..., appointments=appointments)


@appointments.route('/add', methods=['GET', 'POST'])
def add_nurse():
    """
    Add a new appointment
    :return:
    """
    if request.method == 'POST':
        nurse_id = request.form['nurse_id']
        patient_id = request.form['patient_id']
        date = request.form['date']
        care = request.form['care']
        error = None

        if not nurse_id:
            error = 'A nurse_id is required.'
        elif not patient_id:
            error = 'A patient is required.'
        elif not date:
            error = 'Date is required.'
        elif not care:
            error = 'Care is required.'

        else:
            # storing the new appointment information in the db
            appointment = Appointment(nurse_id, patient_id, date, care)
            db.session.add(appointment)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('get_appointments'))

        flash(error)

    return render_template('add_appointment.html')


@appointments.route('/get_appointments/<last_name>/<first_name>',  methods=['GET', 'POST'])
def get_appointments(patient_name):
    if request.method == "POST":

        error = None


    # appointments = Appointment.query.filter().join(Appointment.patient)
    return

