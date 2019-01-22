from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
import re
from sqlalchemy.sql import or_
from dev_log import db
from dev_log.models import Patient
from dev_log.auth.controllers import login_required
from dev_log.auth.controllers import admin_required

patients = Blueprint('patients', __name__, url_prefix='/patients')


@patients.route('/', methods=['GET', 'POST'])
@admin_required
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

    patients = Patient.query.filter(Patient.office == session['office_name']).order_by(Patient.last_name)

    return render_template('patients.html', patients=patients)


@patients.route('/results/<research>', methods=['GET', 'POST'])
@admin_required
def search_patients(research):
    if request.method == "POST":
        new_research = request.form['research']
        error = None

        if not new_research:
            error = 'Please enter the name of our patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('patients.search_patients', research=new_research))

    if len(research.split()) >= 2:
        first_name, last_name = research.split()[0], " ".join(research.split()[1:])
        patients = Patient.query.filter(or_(Patient.last_name.like('%' + last_name + '%'),
                                            Patient.first_name.like('%' + first_name + '%')),
                                        Patient.office == session['office_name'])
    else:
        patients = Patient.query.filter(or_(Patient.last_name.like('%' + research + '%'),
                                            Patient.first_name.like('%' + research + '%')),
                                        Patient.office == session['office_name'])

    if patients is None:
        error = "Please enter a lastname"
        flash(error)

    return render_template('patients.html', patients=patients)


@patients.route('/add_patient', methods=['GET', 'POST'])
@admin_required
def add_patient():
    if request.method == "POST":
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone_number']
        digicode = request.form['digicode']
        additional_postal_information = request.form['additional_postal_information']
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
                              email=email, address=address, phone=phone, digicode=digicode,
                              additional_postal_information=additional_postal_information,
                              office=session['office_name'])
            print("latitude : {}, longitude : {} ".format(patient.latitude, patient.longitude))
            db.session.add(patient)
            db.session.commit()
            flash('The patient was successfully added')
            return redirect(url_for('patients.home'))

        flash(error)

    return render_template('add_patient.html')


@patients.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
@admin_required
def edit_patient(patient_id):

    if request.method == "POST":
        print(request.form)
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone_number']
        digicode = request.form['digicode']
        additional_postal_information = request.form['additional_postal_information']
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
        else:
            db.session.query(Patient).filter(Patient.id == patient_id).\
                update(dict(last_name=last_name,
                       first_name=first_name,
                       email=email,
                       address=address,
                       phone=phone,
                        digicode=digicode,
                        additional_postal_information=additional_postal_information,
                        office=session['office_name']))
            db.session.commit()
            flash("The patient's information have been updated")
            return redirect(url_for('patients.home'))
        flash(error)

    patient = Patient.query.filter(Patient.id == patient_id).first()
    return render_template("edit_patient.html", patient=patient)


@patients.route('/delete_patient/<int:patient_id>')
@admin_required
def delete_patient(patient_id):
    patient = Patient.query.get(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash("The patient was successfully deleted.")

    return redirect(url_for('patients.home'))



