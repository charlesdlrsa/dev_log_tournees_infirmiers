import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dev_log.auth.controllers import auth
from dev_log.patient import controllers
from dev_log.appointments.controllers import appointments


app = Flask(__name__)
app.config.from_object('config')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

app.register_blueprint(auth)
app.register_blueprint(controllers.patient)
app.register_blueprint(appointments)

db.create_all()
# app.run()
