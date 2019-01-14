from flask import Blueprint, request, render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import re
from sqlalchemy.sql import or_
from dev_log import db
from dev_log.models import Nurse, Care
from dev_log.auth.controllers import login_required
from dev_log.auth.controllers import admin_required

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

    nurses = db.session.query(Nurse).order_by(Nurse.last_name).all()
    return render_template('nurses.html', nurses=nurses)


@nurses.route('/results/<research>', methods=['GET', 'POST'])
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
                                        Nurse.first_name.like('%' + first_name + '%')))
    else:
        nurses = Nurse.query.filter(or_(Nurse.last_name.like('%' + research + '%'),
                                        Nurse.first_name.like('%' + research + '%')))
    if nurses is None:
        error = "Please enter a lastname"
        flash(error)

    return render_template('nurses.html', nurses=nurses)


# @nurses.route('/information/<int:nurse_id>', methods=['GET, POST'])
# def get_information_about_nurse(nurse_id):
#     nurse = Nurse.query.filter(Nurse.id == nurse_id)
#     print(nurse.last_name)
#     return render_template("nurse_info.html", nurse=nurse)


@nurses.route('/edit/<int:nurse_id>', methods=['GET', 'POST'])
def edit_nurse(nurse_id):
    print(nurse_id)
    if request.method == "POST":
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        address = request.form['address']
        # office = request.form['office']

        password = generate_password_hash(password)
        db.session.query(Nurse).filter(Nurse.id == nurse_id). \
            update(dict(last_name=last_name,
                        first_name=first_name,
                        email=email,
                        phone=phone,
                        password=password,
                        address=address))
        db.session.commit()
        flash("The nurse's information have been updated")
        return redirect(url_for('nurses.home'))

    nurse = Nurse.query.filter(Nurse.id == nurse_id).first()

    return render_template("edit_nurse.html", nurse=nurse)


@nurses.route('/add_nurse', methods=['GET', 'POST'])
def add_nurse():
    """
    Add a new nurse
    :return:
    """
    if request.method == 'POST':
        print(request.form)
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone_number']
        address = request.form['address']
        office = request.form['office']
        # care = request.form['care']
        #care = Care.query.filter(Care.description == request.form['care']).first().id
        #print(care)
        regu_expr = r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*(\.[a-zA-Z]{2,6})$"
        error = None

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
                          email=email, password=password, phone=phone, address=address, office=office)
            db.session.add(nurse)
            db.session.commit()
            flash('The nurse was successfully added')
            return redirect(url_for('nurses.home'))

        flash(error)

    cares = db.session.query(Care).all()
    print(cares)
    return render_template('add_nurse.html', cares=cares)

