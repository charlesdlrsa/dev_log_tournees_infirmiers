from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
import re
from sqlalchemy.sql import or_
from dev_log import db
from dev_log.models import Nurse, Care
from dev_log.auth.controllers import login_required
from dev_log.auth.controllers import admin_required
from dev_log.key import key


nurses = Blueprint('nurses', __name__, url_prefix='/nurses')


@nurses.route('/', methods=['GET', 'POST'])
@admin_required
def home():
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our nurse.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('nurses.search_nurses', research=research))

    nurses = Nurse.query.filter(Nurse.office == session['office_name']).order_by(Nurse.last_name)
    return render_template('nurses.html', nurses=nurses)


@nurses.route('/results/<research>', methods=['GET', 'POST'])
@admin_required
def search_nurses(research):
    if request.method == "POST":
        new_research = request.form['research']
        error = None

        if not new_research:
            error = 'Please enter the name of a nurse.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('nurses.search_nurses', research=new_research))

    if len(research.split()) >= 2:
        first_name, last_name = research.split()[0], " ".join(research.split()[1:])
        nurses = Nurse.query.filter(or_(Nurse.last_name.like('%' + last_name + '%'),
                                        Nurse.first_name.like('%' + first_name + '%')),
                                    Nurse.office == session['office_name'])
    else:
        nurses = Nurse.query.filter(or_(Nurse.last_name.like('%' + research + '%'),
                                        Nurse.first_name.like('%' + research + '%')),
                                    Nurse.office == session['office_name'])
    if nurses is None:
        error = "Please enter a lastname"
        flash(error)

    return render_template('nurses.html', nurses=nurses)


@nurses.route('/add_nurse', methods=['GET', 'POST'])
def add_nurse():
    """
    Add a new nurse
    :return:
    """
    if request.method == 'POST':
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone_number']
        address = request.form['address']
        care = Care.query.all()
        cares = ""
        for c in care:
            if request.form.get(str(c.id)) is not None:
                cares += "-{}-".format(c.id)
        regu_expr = r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*(\.[a-zA-Z]{2,6})$"

        if not last_name:
            error = 'A lastname is required.'
        elif not first_name:
            error = 'A firstname is required.'
        elif re.search(regu_expr, email) is None:
            error = 'Please enter a correct email address.'
        elif not password:
            error = 'Password is required.'
        elif not phone:
            error = 'Phone is required.'
        elif not address:
            error = 'Please enter an address.'
        elif Nurse.query.filter(Nurse.email == email).first() is not None:
            error = 'The email "{}" is already used'.format(email)

        else:
            # storing the new user information in the db
            password = generate_password_hash(password)
            nurse = Nurse(last_name=last_name, first_name=first_name, email=email, password=password,
                          phone=phone, address=address, office=session['office_name'], cares=cares)
            db.session.add(nurse)
            db.session.commit()
            flash('The nurse was successfully added')
            return redirect(url_for('nurses.home'))

        flash(error)

    cares = db.session.query(Care).all()
    return render_template('add_nurse.html', cares=cares)


@nurses.route('/edit/<int:nurse_id>', methods=['GET', 'POST'])
@admin_required
def edit_nurse(nurse_id):
    if request.method == "POST":
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        phone = request.form['phone_number']
        password = request.form['password']
        address = request.form['address']
        care = Care.query.all()
        cares = ""
        for c in care:
            if request.form.get(str(c.id)) is not None:
                cares += "-{}-".format(c.id)
        regu_expr = r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*(\.[a-zA-Z]{2,6})$"

        if not last_name:
            error = 'A lastname is required.'
        elif not first_name:
            error = 'A firstname is required.'
        elif re.search(regu_expr, email) is None:
            error = 'Please enter a correct email address.'
        elif not password:
            error = 'Password is required.'
        elif not phone:
            error = 'Phone is required.'
        elif not address:
            error = 'Please enter an address.'
        elif Nurse.query.filter(Nurse.email == email).first() is not None:
            error = 'The email "{}" is already used'.format(email)

        else:
            password = generate_password_hash(password)
            db.session.query(Nurse).filter(Nurse.id == nurse_id). \
                update(dict(last_name=last_name,
                            first_name=first_name,
                            email=email,
                            phone=phone,
                            password=password,
                            address=address,
                            office=session['office_name'],
                            cares=cares))
            db.session.commit()
            flash("The nurse's information have been updated")
            return redirect(url_for('nurses.home'))

        flash(error)

    nurse = Nurse.query.filter(Nurse.id == nurse_id).first()
    cares = db.session.query(Care).all()
    return render_template("edit_nurse.html", cares=cares, nurse=nurse)


@nurses.route('/delete_nurse/<int:nurse_id>')
@admin_required
def delete_nurse(nurse_id):
    nurse = Nurse.query.get(nurse_id)
    db.session.delete(nurse)
    db.session.commit()
    flash("The nurse was successfully deleted.")
    return redirect(url_for('nurses.home'))

