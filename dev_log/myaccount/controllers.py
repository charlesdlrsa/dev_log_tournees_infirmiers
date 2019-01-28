import re
from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash
from dev_log import db
import datetime
from dev_log.models import Absence, Office, Nurse, Care
from dev_log.auth.controllers import login_required, admin_required
# from dev_log.nurses.controllers import edit_nurse

account = Blueprint('account', __name__, url_prefix='/account')


@account.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if session.get('office_id') is None:
        id = session['nurse_id']
        nurse = Nurse.query.filter(Nurse.id == id).first()
        return render_template('nurse_account.html', nurse=nurse)
    else:
        id = session['office_id']
        office = Office.query.filter(Office.id == id).first()
        return render_template('office_account.html', office=office)

@account.route('/edit/nurse/<int:nurse_id>', methods=['GET', 'POST'])
@login_required
def edit_nurse_account(nurse_id):
    if request.method == "POST":
        print(request.form)
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        email = request.form['email']
        phone = request.form['phone_number']
        password = request.form['password']
        address = request.form['address']

        care = Care.query.all()
        print(care)
        cares = ""
        for c in care:
            if request.form.get(str(c.id)) is not None:
                cares += "-{}-".format(c.id)
        regu_expr = r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*(\.[a-zA-Z]{2,6})$"
        print(cares)
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

        else:
            password = generate_password_hash(password)
            db.session.query(Nurse).filter(Nurse.id == nurse_id). \
                update(dict(last_name=last_name,
                            first_name=first_name,
                            email=email,
                            phone=phone,
                            password=password,
                            address=address,
                            cares=cares))
            db.session.commit()
            flash("The nurse's information have been updated")
            return redirect(url_for('account.home'))

        flash(error)

    nurse = Nurse.query.filter(Nurse.id == nurse_id).first()
    cares = db.session.query(Care).all()
    return render_template("edit_nurse.html", cares=cares, nurse=nurse)


@account.route('/edit/office/<int:office_id>', methods=['GET', 'POST'])
@admin_required
def edit_office_account(office_id):
    if request.method == "POST":
        print(request.form)
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone_number']
        password = request.form['password']
        address = request.form['address']

        regu_expr = r"^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*(\.[a-zA-Z]{2,6})$"
        if not name:
            error = 'A name is required.'
        elif re.search(regu_expr, email) is None:
            error = 'Please enter a correct email address.'
        elif not password:
            error = 'Password is required.'
        elif not phone:
            error = 'Phone is required.'
        elif not address:
            error = 'Please enter an address.'

        else:
            password = generate_password_hash(password)
            db.session.query(Office).filter(Office.id == office_id). \
                update(dict(name=name,
                            email=email,
                            phone=phone,
                            password=password,
                            address=address))
            db.session.commit()
            flash("The office's information have been updated")
            return redirect(url_for('account.home'))

        flash(error)

    office = Office.query.filter(Office.id == office_id).first()
    return render_template("edit_office.html", office=office)


@account.route('/absence', methods=['GET', 'POST'])
@login_required
def add_absence():
    id = session['nurse_id']
    nurse = Nurse.query.filter(Nurse.id == id).first()
    if request.method == "POST":
        # if True: #demie journée
        #     date = request.form['date']
        #     halfday = request.form['halfday']
        #     absence = Absence(nurse_id=id, date=date, halfday=halfday)
        #     db.session.add(absence)
        # else: #période
        # if request.args.get('period'):
        start_date = datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        days_in_period = []
        if start_date <= end_date:
            for n in range((end_date - start_date).days + 1):
                days_in_period.append(start_date + datetime.timedelta(n))
        else:
            for n in range((start_date - end_date).days + 1):
                days_in_period.append(start_date - datetime.timedelta(n))
        for d in days_in_period:
            for halfday in ['Morning', 'Afternoon']:
                absence = Absence(nurse_id=id, date=d, halfday=halfday)
                db.session.add(absence)
                db.session.commit()
            flash("This absence has been added")
        return redirect(url_for('account.home'))
    nurse = db.session.query(Nurse).filter(Nurse.id == id)[0]
    return render_template('add_vacation.html', nurse=nurse)


def edit_admin(id):
    name = request.form['name']
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
