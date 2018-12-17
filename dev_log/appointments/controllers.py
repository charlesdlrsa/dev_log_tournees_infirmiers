from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from dev_log import db
from dev_log.models import Appointment

appointments = Blueprint('appointments', __name__, url_prefix='/appointments')


@appointments.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        last_name = request.last_name
        first_name = request.first_name

        return redirect(url_for(appointments.get_appointments, last_name=last_name, first_name=first_name))

    appointments = Appointment.query.all()
    return render_template(..., appointments=appointments)


@appointments.route('/add_appointment', methods=['GET', 'POST'])
def get_appointment():

    if request.method == "POST":
        date = request.date
        care = request.care
        patient_last_name = request.patient_last_name
        patient_first_name = request.patient_first_name

        flash(error)

    return render_template(...)


@appointments.route('/get_appointments/<str:last_name>/<str:first_name>',  methods=['GET', 'POST'])
def get_appointments(last_name, first_name):

    return

