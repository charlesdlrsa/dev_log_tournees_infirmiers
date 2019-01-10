from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

home = Blueprint('home', __name__)


@home.route("/")
def index():
    return render_template("index.html")