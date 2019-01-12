from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from dev_log.models import init_db
from datetime import datetime,timedelta

home = Blueprint('home', __name__)


@home.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        init_db()
    date = datetime.now()
    start_week=date - timedelta(date.weekday())
    end_week = start_week + timedelta(6)
    start_week = str(start_week.day) + '/' + str(start_week.month)
    end_week = str(end_week.day) + '/' + str(end_week.month)
    return render_template("landing.html",
    start_week=start_week,
    end_week=end_week,
    date=date)




