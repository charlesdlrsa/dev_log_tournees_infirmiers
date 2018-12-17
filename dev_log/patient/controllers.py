from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from dev_log import db
from dev_log.models import Patient

patient = Blueprint('patient', __name__, url_prefix='/patient')


@patient.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('patient.get_patients', research=research))

    patients = Patient.query.all()

    return render_template(...., patients=patients)


@patient.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == "POST":
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        address = request.form['address']
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
            patient = Patient(last_name, first_name, email, address)
            db.session.add(patient)
            db.session.commit()
            flash('Patient was successfully added')
            return redirect(url_for('patient.home'))

        flash(error)

    return render_template(...)


@patient.route('/get_patients/<str:research>', methods=['GET', 'POST'])
def get_patients(research):

    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('patient.get_patients', research=research))

    patients = Patient.query.filter(or_(Patient.last_name == research,Patient.first_name == research)).all()
    if patients is None:
        error = "Please enter a lastname"
    flash(error)
    return render_template(..., patients=patients)