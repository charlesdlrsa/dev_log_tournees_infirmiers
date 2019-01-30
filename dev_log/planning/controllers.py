from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from dev_log.models import init_db
import datetime
from dev_log.auth.controllers import login_required
from dev_log.auth.controllers import admin_required
from dev_log.utils.calendar import *
from dev_log.models import Appointment, Patient, Nurse, Care, Office
from dev_log import db

planning = Blueprint('planning', __name__, url_prefix='/planning')


@planning.route("/", methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        if session.get('nurse_id') is not None:
            nurse_id = session.get('nurse_id')
        else:
            nurse_id = request.form['input_nurse']
        date = request.form['date']
        halfday = request.form['halfday']
        error = None

        if nurse_id == "":
            error = "You need to select a nurse to view a planning"
        elif halfday == "":
            error = "You need to select a halfday"
        if error is not None:
            flash(error)
        else:
            return redirect(url_for('planning.get_nurse_planning', nurse_id=nurse_id, date=date, halfday=halfday))

    if session.get('office_id'):
        nurses = Nurse.query.filter(Nurse.office_id == session['office_id'])
    else:
        nurses = Nurse.query.filter(Nurse.id == session.get('nurse_id')).first()

    return render_template("planning_home.html", nurses=nurses)


@planning.route('/<int:nurse_id>/<date>/<halfday>', methods=['GET', 'POST'])
@login_required
def get_nurse_planning(nurse_id, date, halfday):
    if request.method == "POST":
        pass

    departure = {'lat': 48.81, 'lng': 2.34}
    arrival = {'lat': 48.83, 'lng': 2.36}
    travel_mode = 'DRIVING'

    return render_template("planning_nurse.html", departure=departure, arrival=arrival, travel_mode=travel_mode,
                           date=date, halfday=halfday)


@planning.route("/init", methods=['GET', 'POST'])
@admin_required
def reinit_db():
    init_db()
    return redirect(url_for("planning.home"))
