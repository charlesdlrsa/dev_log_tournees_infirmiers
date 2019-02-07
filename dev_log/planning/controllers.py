from flask import Blueprint, request, render_template, flash, session, redirect, url_for
from dev_log.init_database import init_db
from dev_log.auth.controllers import login_required, admin_required
from dev_log.models import Nurse, Schedule, Office
from dev_log.utils import calendar
import datetime

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
        date_selected = calendar.get_dates_from_form(date)[0]
        halfday = request.form['halfday']
        error = None

        if nurse_id == "":
            error = "You need to select a nurse to view a planning"
        elif halfday == "":
            error = "You need to select a halfday"
        elif date_selected > datetime.date.today() + datetime.timedelta(1):
            error = "You cannot see a nurse planning more than 24 hours before the desired date."
            pass
        if error is not None:
            flash(error)
        else:
            return redirect(url_for('planning.get_nurse_planning', nurse_id=nurse_id, date=date, halfday=halfday))

    if session.get('office_id'):
        nurses = Nurse.query.filter(Nurse.office_id == session['office_id'])
    else:
        nurses = None

    return render_template("planning_home.html", nurses=nurses)


@planning.route('/nurse-<int:nurse_id>/date-<date>/<halfday>', methods=['GET', 'POST'])
@login_required
def get_nurse_planning(nurse_id, date, halfday):
    if request.method == 'POST':
        pass

    nurse = Nurse.query.get(nurse_id)
    date_selected = calendar.get_dates_from_form(date)[0]

    office = Office.query.filter(Office.id == nurse.office_id).all()
    schedules = Schedule.query.filter(Schedule.nurse_id == nurse_id,
                                      Schedule.appointment.has(date=date_selected),
                                      Schedule.appointment.has(halfday=halfday)).all()
    if len(schedules) == 0:
        # TODO : à changer par la vraie fonction de Romu
        # run Romuald's optimizer to set the schedules before requesting schedules' database
        schedules = Schedule.query.filter(Schedule.nurse_id == nurse_id,
                                          Schedule.appointment.has(date=date_selected),
                                          Schedule.appointment.has(halfday=halfday)).all()
    if halfday == "Morning":
        schedules = office + schedules
        nb_schedules = len(schedules)
    else:
        schedules = schedules + office
        nb_schedules = len(schedules)

    return render_template("planning_nurse.html", nurse=nurse, date=date_selected, halfday=halfday,
                           schedules=schedules, nb_schedules=nb_schedules)


@planning.route("/init", methods=['GET', 'POST'])
@admin_required
def reinit_db():
    """
    Initializes the database on click
    """
    init_db()
    message = "The database has been reinitialised"
    flash(message)
    return redirect(url_for("planning.home"))
