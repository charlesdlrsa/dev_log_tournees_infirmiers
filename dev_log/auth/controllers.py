from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import re
from dev_log import db
from dev_log.models import Nurse, Office
import functools

auth = Blueprint('auth', __name__, url_prefix='/auth')

#
# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     """
#     View of the register page, handles the register form
#     :return:
#     """
#     if request.method == 'POST':
#         last_name = request.form['last_name']
#         first_name = request.form['first_name']
#         email = request.form['email']
#         password = request.form['password']
#         address = request.form['address']
#         error = None
#         regu_expr = r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*(\.[a-zA-Z]{2,6})$"
#
#         if not last_name:
#             error = 'A lastname is required.'
#         elif not first_name:
#             error = 'A firstname is required.'
#         elif re.search(regu_expr, email) is None:
#             error = 'Please enter a correct email address.'
#         elif not password:
#             error = 'Password is required.'
#         elif not address:
#             error = 'Please enter an address.'
#         elif Nurse.query.filter(Nurse.email == email).first() is not None:
#             error = 'The email "{}" is already used'.format(email)
#             print(error)
#
#         else:
#             # storing the new user information in the db
#             print("Storing new user")
#             password = generate_password_hash(password)
#             nurse = Nurse(last_name, first_name, email, password, address)
#             db.session.add(nurse)
#             db.session.commit()
#             flash('Record was successfully added')
#             return redirect(url_for('auth.login'))
#
#         flash(error)
#
#     return render_template('register.html')


@auth.route('/login', methods=('GET', 'POST'))
def login():
    """
    View of the login page, handles the users connections
    :return:
    """
    if request.method == 'POST':
        user_type = request.form['user-type']
        email = request.form['email']
        password = request.form['password']
        error = None
        if user_type == "nurse":
            nurse = Nurse.query.filter(Nurse.email == email).first()
            if nurse is None:
                error = 'Incorrect email address.'
            elif not check_password_hash(nurse.password, password):
                error = 'Incorrect password.'

            if error is None:
                # storing user information in the object "session"
                session.clear()
                session['nurse_id'] = nurse.id
                session['nurse_last_name'] = nurse.last_name
                session['nurse_first_name'] = nurse.first_name
                session['nurse_email'] = nurse.email
                session['nurse_phone_number'] = nurse.phone
                session['nurse_office'] = nurse.office
                session['nurse_address'] = nurse.address
                flash('Hi %s %s, welcome back to Our Application!'
                      % (nurse.first_name.capitalize(),
                         nurse.last_name.capitalize()))

        elif user_type == 'admin':
            office = Office.query.filter(Office.email == email).first()

            if office is None:
                error = 'Incorrect email address.'
            elif not check_password_hash(office.password, password):
                error = 'Incorrect password.'

            if error is None:
                # storing user information in the object "session"
                session.clear()
                session['office_id'] = office.id
                session['office_name'] = office.name
                flash('Hi %s %s, welcome back to Our Application!'
                      % (office.name.capitalize()))

            return redirect(url_for("home.index"))

        else:
            error = "Please select a user type"

        flash(error)
        return render_template('landing.html')

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    """
    Logs out the user by cleaning the session user and redirects to the homepage
    :return:
    """
    session.clear()
    return redirect(url_for('home.index'))


def login_required(view):
    """
    Decorator that will check if a user is signed in and redirect him to the sign in page if not
    :param view:
    :return:
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('nurse_id') is None:
            flash('You need to login as a nurse to access this page.')
            return redirect(request.referrer)

        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    """
    Decorator that will check if a user is signed in and redirect him to the sign in page if not
    :param view:
    :return:
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('office_id') is None:
            flash('You need to login as an administrator to access this page.')
            return redirect(request.referrer)

        return view(**kwargs)

    return wrapped_view
