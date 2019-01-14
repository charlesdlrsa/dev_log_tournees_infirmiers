from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from dev_log.models import init_db
from datetime import datetime,timedelta
from dev_log.auth.controllers import login_required
from dev_log.auth.controllers import admin_required
from dev_log.utils.calendar import *
import datetime
from dev_log.utils.calendar import *

planning = Blueprint('planning', __name__, url_prefix='/planning')


@planning.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        print('lol')
    if "week" in request.args:
        week=int(request.args['week'])
        year=int(request.args['year'])
        if week==0:
            week=52
            year=year-1
        elif week==53:
            week=1
            year=year+1
    else:
        current_date = datetime.datetime.now().date()
        week = current_date.isocalendar()[1]
        year = current_date.isocalendar()[0]
    start_week=iso_to_gregorian(year,week,1)
    end_week=iso_to_gregorian(year,week,7)
    start_week = str(start_week.day) + '/' + str(start_week.month)
    end_week = str(end_week.day) + '/' + str(end_week.month)
    return render_template("landing.html",
    start_week=start_week,
    end_week=end_week,
    year=year,
    week=week)








