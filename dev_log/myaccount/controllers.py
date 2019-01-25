from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from dev_log import db
import datetime
from dev_log.models import Absence, Office, Nurse
from dev_log.auth.controllers import login_required
from dev_log.nurses.controllers import edit_nurse

account = Blueprint('account', __name__, url_prefix='/account')


@account.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if session.get('office_id') is None:
        id = session['nurse_id']
        # créer l'objet nurse
    else:
        id = session['office_id']

        if request.method == "POST":
            if session.get('office_id') is None:
                id = session['nurse_id']
                if request.args(edit):
                    edit_nurse(id)
                elif request.args(vacances):
                    return redirect(url_for('account.add_absence'))
            else:
                id = session['office_id']
                return redirect(url_for('account.edit_account', id=id))
    return render_template('account.html', id=id)


@account.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_account(id):
    if session.get('nurse_id') is not None:
        edit_nurse(id)
    elif session.get('office_id') is not None:
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

        return redirect(url_for('account.home'))


@account.route('/absence', methods=['GET', 'POST'])
@login_required
def add_absence():
    id = session['nurse_id']
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

# def absence():
#     id = 1
#     nurse = db.session.query(Nurse).filter(Nurse.id == id)[0]
#     return render_template('add_vacation.html', nurse=nurse)
