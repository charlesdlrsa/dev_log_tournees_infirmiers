from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from dev_log.models import init_db
from datetime import datetime, timedelta
from dev_log.auth.controllers import login_required
from dev_log.auth.controllers import admin_required
from dev_log.utils.calendar import *
from dev_log.utils.calendar import *
from dev_log.models import Appointment, Patient, Nurse, Care, Office
from dev_log import db

planning = Blueprint('planning', __name__, url_prefix='/planning')


@planning.route("/", methods=['GET', 'POST'])
@admin_required
def home():
    if request.method == "POST":
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

    current_date = datetime.datetime.now()
    day = current_date.isocalendar()[2]
    week = current_date.isocalendar()[1]
    year = current_date.isocalendar()[0]
    time = iso_to_gregorian(year, week, day)
    time = time.strftime('%Y-%m-%d')

    nurses = Nurse.query.filter(Nurse.office_id == session['office_id'])

    return render_template("planning.html", nurses=nurses, time=time)


@planning.route('/<int:nurse_id>/<date>/<halfday>', methods=['GET', 'POST'])
def get_nurse_planning(nurse_id, date, halfday):
    if request.method == "POST":
        customer_1 = request.args('customer_1')
        customer_2 = request.args('customer_2')

    customer_1 = None
    customer_2 = None
    return render_template("map_planning.html", customer_1=customer_1, customer_2=customer_2)



# @planning.route("/", methods=['GET', 'POST'])
# def home():
#     if request.method == "POST":
#         if "date" in request.form.keys():
#             date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d').date()
#         else:
#             date = None
#         return redirect(url_for('planning.home',date=date,nurse_research=nurse_research))
#     # if "week" in request.args:
#     #     week=int(request.args['week'])
#     #     year=int(request.args['year'])
#     #     if week==0:
#     #         week=52
#     #         year=year-1
#     #     elif week==53:
#     #         week=1
#     #         year=year+1
#     if "date" in request.args:
#         current_date = datetime.datetime.strptime(request.args['date'], '%Y-%m-%d').date()
#     else:
#         current_date = datetime.datetime.now()
#     day = 1
#     if "nurse_research" in request.args:
#         if request.args["nurse_research"] != "Choose Nurse":
#             nurse_research = request.args["nurse_research"]
#         else:
#             nurse_research = None
#     else:
#         nurse_research = None
#     ############ Insert filter on appointments
#     week = current_date.isocalendar()[1]
#     year = current_date.isocalendar()[0]
#     time = iso_to_gregorian(year, week, day)
#     time = time.strftime('%Y-%m-%d')
#     start_week=iso_to_gregorian(year,week,1)
#     end_week=iso_to_gregorian(year,week,7)
#     start_week = str(start_week.day) + '/' + str(start_week.month)
#     end_week = str(end_week.day) + '/' + str(end_week.month)
#     nurses = db.session.query(Nurse).all()
#
#     return render_template("landing.html", start_week=start_week, end_week=end_week, year=year, week=week, time=time,
#                            nurses=nurses, nurse_research=nurse_research)


@planning.route("/init", methods=['GET', 'POST'])
def reinit_db():
    init_db()
    return redirect(url_for("planning.home"))






