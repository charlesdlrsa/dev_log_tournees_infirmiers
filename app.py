import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

import dev_log.auth as auth
import dev_log.patient as patient
import dev_log.nurses as nurse
import dev_log.appointments as appointments


app = Flask(__name__)
app.config.from_object('config')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

app.register_blueprint(auth.bp)
app.register_blueprint(patient.bp)
app.register_blueprint(nurse.bp)
app.register_blueprint(appointments.bp)

db.create_all()
# app.run()
