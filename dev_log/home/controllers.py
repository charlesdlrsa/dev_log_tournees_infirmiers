from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from dev_log.models import init_db

home = Blueprint('home', __name__)


@home.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        init_db()
    return render_template("landing.html")
