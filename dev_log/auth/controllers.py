from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug.security import check_password_hash
from dev_log.models import Nurse, Office
import functools

auth = Blueprint('auth', __name__)


@auth.route('/', methods=('GET', 'POST'))
@auth.route('/auth/login', methods=('GET', 'POST'))
def login():
    """ View of the login page, handles the users connections """

    if request.method == 'GET':
        pass
        # init_db()
    if request.method == 'POST':
        user_type = request.form['user-type']
        email = request.form['email']
        password = request.form['password']
        error = None
        if user_type == "nurse":
            nurse = Nurse.query.filter(Nurse.email == email).first()
            if nurse is None:
                error = 'Incorrect email address or user type.'
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
                session['nurse_office_id'] = nurse.office_id
                session['nurse_address'] = nurse.address
                flash('Hi %s %s, welcome back to Our Application!'
                      % (nurse.first_name,
                         nurse.last_name.capitalize()))

                return redirect(url_for("planning.home"))
            flash(error)
            return redirect(request.referrer)

        elif user_type == 'admin':
            office = Office.query.filter(Office.email == email).first()

            if office is None:
                error = 'Incorrect email address or user type.'
            elif not check_password_hash(office.password, password):
                error = 'Incorrect password.'

            if error is None:
                # storing user information in the object "session"
                session.clear()
                session['office_id'] = office.id
                session['office_name'] = office.name
                flash('Hi %s, welcome back to Our Application!'
                      % (office.name.capitalize()))

                return redirect(url_for("planning.home"))
            flash(error)
            return redirect(request.referrer)

        else:
            error = "Please select a user type"

        flash(error)
        return redirect(request.referrer)

    return render_template('login.html')


def login_required(view):
    """ Decorator that will check if a nurse or an admin is signed in and redirect him to the sign in page if not """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('nurse_id') is None \
                and session.get('office_id') is None:
            flash('You need to login as a nurse to access the precedent page.')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    """ Decorator that will check if an admin is signed in and redirect him to the sign in page if not """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('office_id') is None:
            flash('You need to login as an administrator to access the precedent page.')
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@auth.route('/auth/logout')
@login_required
def logout():
    """ Logs out the user by cleaning the session user and redirects to the homepage """

    session.clear()
    return redirect(url_for('auth.login'))
