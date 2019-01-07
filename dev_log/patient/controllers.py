from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
import re
from sqlalchemy.sql import or_
from dev_log import db
from dev_log.models import Patient

patients = Blueprint('patients', __name__, url_prefix='/patients')


@patients.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of the patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('get_patients', research=research))

    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)


@patients.route('/edit/<int:patient_id>', methods=['GET','POST'])
def edit_patient(patient_id):
    if request.method == "POST":
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        db.session.query(Patient).filter(Patient.id == patient_id).\
            update(last_name=last_name,
                   first_name=first_name,
                   email=email,
                   phone=phone,
                   address=address)

    patient = Patient.query.filter(Patient.id == patient_id)
    return render_template('patient_by_id.html', patient=patient)


@patients.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == "POST":
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        address = request.form['address']
        # TODO : requete API pour latitude et longitude
        phone = request.form['phone']
        error = None
        regu_expr = r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*(\.[a-zA-Z]{2,6})$"

        if not last_name:
            error = 'A lastname is required.'
        elif not first_name:
            error = 'A firstname is required.'
        elif re.search(regu_expr, email) is None:
            error = 'Please enter a correct email address.'
        elif not address:
            error = 'Please enter an address.'
        elif Patient.query.filter(Patient.email == email).first() is not None:
            error = 'The email "{}" is already used'.format(email)

        else:
            # storing the new user information in the db
            patient = Patient(last_name, first_name, email, address, latitude, longitude, phone)
            db.session.add(patient)
            db.session.commit()
            flash('Patient was successfully added')
            return redirect(url_for('home'))

        flash(error)

    return render_template('add_patient.html')


@patients.route('/get_patients/<research>', methods=['GET', 'POST'])
def get_patients(research):
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('get_patients', research=research))

    patients = Patient.query.filter(or_(Patient.last_name.like(research + '%'),
                                        Patient.first_name.like(research + '%'))).all()
    if patients is None:
        error = "Please enter a lastname"
        flash(error)
    return render_template('patients.html', patients=patients)
