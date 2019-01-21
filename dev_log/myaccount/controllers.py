from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
import re
from sqlalchemy.sql import or_
from dev_log import db
from dev_log.models import Absence, Nurse, Care, Office
from dev_log.auth.controllers import login_required

account = Blueprint('account', __name__, url_prefix='/account')


@account.route('/edit', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        if session.get('office_id') is None:
            id = session['nurse_id']
        else:
            id = session['office_id']
        return redirect(url_for('account.edit_account', id=id))
    return render_template('account.html')


@account.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_account(id):
    if session.get('nurse_id') is not None:
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        address = request.form['address']
        office = request.form['office']
        care = Care.query.all()
        cares = ""
        for c in care:
            if request.form.get(str(c.id)) is not None:
                cares += "-{}-".format(c.id)
        error = None

        password = generate_password_hash(password)
        db.session.query(Nurse).filter(Nurse.id == id). \
            update(dict(last_name=last_name,
                        first_name=first_name,
                        email=email,
                        phone=phone,
                        password=password,
                        address=address))
        db.session.commit()
        flash("Your information have been updated")

    elif session.get('office_id') is not None:
        name = request.form ['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        address = request.form['address']

        password = generate_password_hash(password)
        db.session.query(Office).filter(Office.id == id). \
            update(dict(name=name,
                        email=email,
                        phone=phone,
                        password=password,
                        address=address))
        db.session.commit()
        flash("The office's information have been updated")

    return redirect(url_for('account.home'))


@account.route('/absence', methods=['GET', 'POST'])
@login_required
def absence():
    pass