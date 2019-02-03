from flask import Blueprint, request, render_template, flash, session, redirect, url_for
from dev_log.models import init_db
from dev_log.auth.controllers import login_required, admin_required
from dev_log.models import Nurse, Patient, Schedule, Appointment
from dev_log.utils import calendar

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
        nurses = None

    return render_template("planning_home.html", nurses=nurses)


@planning.route('/<int:nurse_id>/<date>/<halfday>', methods=['GET', 'POST'])
@login_required
def get_nurse_planning(nurse_id, date, halfday):
    if request.method == 'POST':
        pass

    nurse = Nurse.query.filter(Nurse.id == nurse_id).first()
    date_selected = calendar.get_dates_from_form(date)[0]

    # TO DO : à changer par la vraie fonction de Romu
    schedules = Patient.query.all()[:5]
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
