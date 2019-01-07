from flask import Blueprint, request, render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import re
from sqlalchemy.sql import or_
from dev_log import db
from dev_log.models import Nurse

nurse = Blueprint('nurse', __name__, url_prefix='/nurse')


@nurse.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our nurse.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('get_nurses', research=research))

    nurses = Nurse.query.all()

    return render_template('nurses.html', nurses=nurses)


@nurse.route('/add_nurse', methods=['GET', 'POST'])
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
        phone = request.form ['phone']
        address = request.form['address']
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
        elif Nurse.query.filter(Nurse.email == email).first() is not None:
            error = 'The email "{}" is already used'.format(email)

        else:
            # storing the new user information in the db
            password = generate_password_hash(password)
            nurse = Nurse(last_name, first_name, email, password, phone, address)
            db.session.add(nurse)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('get_nurses'))

        flash(error)

    return render_template('add_nurse.html')


@nurse.route('/edit/<int:nurse_id>', methods=['PUT'])
def edit_nurse(nurse_id):
    # try:
    last_name = request.form['last_name']
    first_name = request.form['first_name']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']
    address = request.form['address']

    db.session.query(Nurse).filter(Nurse.id == nurse_id).\
        update(last_name=last_name, first_name=first_name, email=email,
               password=password, phone=phone, address=address)
    # except as e:
    #     pass


@nurse.route('/get_nurses/<research>', methods=['GET', 'POST'])
def get_nurses(research):
    if request.method == "POST":
        research = request.form['research']
        error = None

        if not research:
            error = 'Please enter the name of our patient.'

        if error is not None:
            flash(error)
        else:
            return redirect(url_for('get_nurses', research=research))

    nurses = Nurse.query.filter(or_(Nurse.last_name == research,
                                    Nurse.first_name == research)).all()
    if nurses is None:
        error = "Please enter a lastname"
        flash(error)
    return render_template('nurses.html')
