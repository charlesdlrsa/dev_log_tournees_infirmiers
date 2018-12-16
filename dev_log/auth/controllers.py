from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import re

from dev_log import db
from dev_log.models import Nurse

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    View of the register page, handles the register form
    :return:
    """
    if request.method == 'POST':
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        error = None
        regu_expr = r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*(\.[a-zA-Z]{2,6})$"

        if not last_name:
            error = 'A lastname is required.'
        if not first_name:
            error = 'A firstname is required.'
        if re.search(regu_expr, email) is None:
            error = 'Please enter a correct email address.'
        if not password:
            error = 'Password is required.'
        if not address:
            error = 'Please enter an address.'
        if Nurse.query.filter_by(email=email).one_or_none() is not None:
            error = 'The email "{}" is already used'.format(email)
            print(error)

        if error is None:
            # storing the new user information in the db
            nurse = Nurse(last_name, first_name, email, password, address)
            db.session.add(nurse)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('auth.login'))

        print("on y va")
        flash(error)
        print("done")

    return render_template('auth/register.html')


@auth.route('/login', methods=('GET', 'POST'))
def login():
    """
    View of the login page, handles the users connections
    :return:
    """
    if request.method == 'POST':
        print("goo")
        email = request.form['username']
        print("email ok")
        password = request.form['password']
        print("pw ok")
        error = None
        infirmier = Nurse.query.filter_by(email=email).one_or_none()
        print("type {}".format(type(infirmier)))
        print(infirmier.last_name)

        if infirmier is None:
            error = 'Incorrect email address.'
        # elif not check_password_hash(infirmier.password, password):
        #     error = 'Incorrect password.'

        if error is None:
            # storing user information in the object "session"
            session.clear()
            session['nurse_id'] = infirmier['id']
            session['nurse_last_name'] = infirmier['last_name']
            session['nurse_first_name'] = infirmier['first_name']
            flash('Hi %s %s, welcome back to Our Application!'
                  % (infirmier['first_name'].capitalize(),
                     infirmier['last_name'].capitalize()))
            return redirect(url_for('search.search'))

        flash(error)

    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    """
    Logs out the user by cleaning the session user and redirects to the homepage
    :return:
    """
    session.clear()
    return redirect(url_for('search.search'))


def login_required(view):
    """
    Decorator that will check if a user is signed in and redirect him to the sign in page if not
    :param view:
    :return:
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('infirmier_id') is None:
            flash('You need to sign in to access this page.')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
