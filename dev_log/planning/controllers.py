from flask import Blueprint, request, render_template, flash, session, redirect, url_for
from dev_log.init_database import init_db
from dev_log.auth.controllers import login_required, admin_required
from dev_log.models import Nurse, Schedule, Office
from dev_log.utils import calendar
import datetime
from dev_log import db
from dev_log.utils.optimizer_functions import build_data_for_optimizer
from dev_log.optim.space import solve_complete, solve_path, GmapApiError

planning = Blueprint('planning', __name__, url_prefix='/planning')


@planning.route("/", methods=['GET', 'POST'])
def home():
    """ Planning's home page allowing to search a nurse planning or your planning if your are logged in as a nurse """

    if request.method == "POST":
        if session.get('nurse_id') is not None:
            nurse_id = session.get('nurse_id')
        else:
            nurse_id = request.form['input_nurse']
        date = request.form['date']
        date_selected = calendar.get_dates_from_form(date)[0]
        # Function available in the module "calendar" in devlog.utils
        # It returns, in date format, the date of the selected day.
        halfday = request.form['halfday']
        error = None

        if nurse_id == "":
            error = "You need to select a nurse to view a planning"
        elif halfday == "":
            error = "You need to select a halfday"
        elif date is None:
            error = "You need to select a date"
        elif date_selected > datetime.date.today() + datetime.timedelta(1) and \
                not (date_selected == datetime.date(2019, 5, 2) and halfday == "Morning"):
            error = "You cannot see a nurse planning more than 24 hours before the desired date."
            # This is due to our optimizer. To set all the appointments to the nurses and optimize their journeys,
            # we need to have all the appointments of the selected half-day. Yet, we can add appointments until 24 hours
            # before a day. Therefore, we must wait that all the possible appointments had been added to launch
            # the optimizer and show the planning of each nurse.

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
    """ Function allowing to get the appointments of a nurse for a specific half-day """

    if request.method == 'POST':
        pass

    nurse = Nurse.query.get(nurse_id)
    date_selected = calendar.get_dates_from_form(date)[0]
    # Function available in the module "calendar" in devlog.utils
    # It returns, in date format, the date of the selected day.

    office = Office.query.filter(Office.id == nurse.office_id).all()
    schedules = Schedule.query.filter(Schedule.appointment.has(date=date_selected),
                                      Schedule.appointment.has(halfday=halfday)).all()

    # If no schedules are planned, it means that it's the first time that the nurse can see its planning.
    # Consequently, we have to run the optimizer to attribute all the appointments to the available nurses
    # and optimize their journeys. If schedules are already planned, this means that the optimizer had already been
    # launched, so the schedules are set for the half-day and we don't need to call the optimizer.
    if len(schedules) == 0:
        nurses_and_appointments = build_data_for_optimizer(date, halfday)
        if nurses_and_appointments["appointments"] == []:
            # no appointments have been scheduled, no need to run the optimizer
            pass
        else:
            try:
                schedules_information = solve_complete(nurses_and_appointments)
                travel_information = simplified_path(nurses_and_appointments)
            except GmapApiError:
                error = "You need to be connected to see the planning. Please check your network connexion " \
                        "and try again."
                flash(error)
                return redirect(url_for('planning.home'))

            for (i, info) in enumerate(schedules_information):
                travel_mode = travel_information[i]["mode"].upper()
                db.session.add(
                    Schedule(appointment_id=int(info["app_id"]),
                             hour=datetime.time(int(info["hour"][:2]), int(info["hour"][3:5])),
                             nurse_id=int(info["nurse_id"]), travel_mode=travel_mode))
                db.session.commit()

    schedules = Schedule.query.filter(Schedule.nurse_id == nurse_id,
                                      Schedule.appointment.has(date=date_selected),
                                      Schedule.appointment.has(halfday=halfday)).all()

    schedules = office + schedules + office
    nb_schedules = len(schedules)

    return render_template("planning_nurse.html", nurse=nurse, date=date_selected, halfday=halfday,
                           schedules=schedules, nb_schedules=nb_schedules)


@planning.route("/init_db", methods=['GET', 'POST'])
def reinit_db():
    """ Initializes the database on click """

    init_db()
    message = "The database has been reinitialised"
    flash(message)
    return redirect(url_for("planning.home"))


def simplified_path(data):
    """ Transform the output of the function solve_path to extract the travel modes.
    The solve_path function returns all the steps that the nurse has to follow during the half-day."""

    path = solve_path(data)
    res = []
    already_visited = []
    for i in path:
        if i["mode"] == 'driving':
            res.append(i)
            already_visited.append((i['t_lat'], i['t_lon']))
        else:
            if (i['t_lat'], i['t_lon']) in already_visited:
                pass
            else:
                res.append(i)
                already_visited.append((i['t_lat'], i['t_lon']))
    return res
