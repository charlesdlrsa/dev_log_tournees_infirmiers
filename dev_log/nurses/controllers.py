from flask import Blueprint, request, render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import re
from sqlalchemy.sql import or_
from dev_log import db
from dev_log.models import Nurse

nurses = Blueprint('nurses', __name__, url_prefix='/nurses')


@nurses.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our nurse.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('get_list_of_nurses', research=research))

    nurses = Nurse.query.all()
    for nurse in nurses:
        print(nurse.__dict__)
    return render_template('nurses.html', nurses=nurses)


@nurses.route('/results/<research>', methods=['GET', 'POST'])
def get_list_of_nurses(research):
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('get_nurses', research=research))

    nurses = Nurse.query.filter(or_(Nurse.last_name.like(research+'%'),
                                    Nurse.first_name.like(      research+'%'))).all()
    if nurses is None:
        error = "Please enter a lastname"
        flash(error)

    return render_template('nurses.html', nurses=nurses)


@nurses.route('/information/<int:nurse_id>', methods=['GET, POST'])
def get_information_about_nurse(nurse_id):
    nurse = Nurse.query.filter(Nurse.id == nurse_id)
    print(nurse.last_name)
    return render_template("nurse_info.html", nurse=nurse)


@nurses.route('/edit/<int:nurse_id>', methods=['PUT'])
def edit_nurse(nurse_id):
    if request.method == "POST":
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']

        db.session.query(Nurse).filter(Nurse.id == nurse_id).\
            update(last_name=last_name, first_name=first_name, email=email,
                   password=password, phone=phone, address=address)

        return redirect(url_for('get_information_about_nurse', nurse_id=nurse_id))

    nurse = Nurse.query.filter(Nurse.id == nurse_id)

    return render_template("edit_nurse.html", nurse=nurse)


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
        office = request.form['office']
        error = None
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
        elif not office:
            error = 'Please enter an office.'
        elif Nurse.query.filter(Nurse.email == email).first() is not None:
            error = 'The email "{}" is already used'.format(email)

        else:
            # storing the new user information in the db
            password = generate_password_hash(password)
            nurse = Nurse(last_name=last_name, first_name=first_name,
                          email=email, password=password, phone=phone, address=address)
            db.session.add(nurse)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('nurses.home'))

        flash(error)

    return render_template('add_nurse.html')

