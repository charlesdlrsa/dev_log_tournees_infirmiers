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
            error = 'Please enter the name of your patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('patients.search_patients', research=research))

    patients = db.session.query(Patient).order_by(Patient.last_name).all()

    return render_template('patients.html', patients=patients)


@patients.route('/results/<research>', methods=['GET', 'POST'])
def search_patients(research):
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('patients.search_patients', research=research))



    patients = Patient.query.filter(or_(Patient.last_name.like(research+'%'),
                                        Patient.first_name.like(research+'%'))).all()

    if patients is None:
        error = "Please enter a lastname"
        flash(error)

    return render_template('patients.html', patients=patients)


# @patients.route('/information/<int:patient_id>', methods=['GET, POST'])
# def get_information_about_patient(patient_id):
#     patient = Patient.query.filter(Patient.id == patient_id)
#
#     return render_template("patient_information.html", patient=patient)


@patients.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):

    if request.method == "POST":
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']
        db.session.query(Patient).filter(Patient.id == patient_id).\
            update(dict(last_name=last_name,
                   first_name=first_name,
                   email=email,
                   address=address,
                   phone=phone))
        db.session.commit()
        flash("The patient's information have been updated")
        return redirect(url_for('patients.home'))

    patient = Patient.query.filter(Patient.id == patient_id).first()
    print(patient.phone)
    return render_template("edit_patient.html", patient=patient)


@patients.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == "POST":
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone_number']
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
        elif not phone:
            error = 'Phone is required.'
        elif Patient.query.filter(Patient.email == email).first() is not None:
            error = 'The email "{}" is already used'.format(email)

        else:
            # storing the new user information in the db
            patient = Patient(last_name=last_name, first_name=first_name,
                              email=email, address=address, phone=phone)
            db.session.add(patient)
            db.session.commit()
            flash('The patient was successfully added')
            return redirect(url_for('patients.home'))

        flash(error)

    return render_template('add_patient.html')



