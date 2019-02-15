from pkg_resources import get_distribution, DistributionNotFound

# The right way of setting project version
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Config options
app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']

# Checking if initialisation is necessary
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_path = os.path.join(BASE_DIR, 'database.db')
existing_database = os.path.exists(db_path)

# Create database connection object
db = SQLAlchemy(app)

from dev_log.planning.controllers import planning
app.register_blueprint(planning)

from dev_log.auth.controllers import auth
app.register_blueprint(auth)

from dev_log.nurses.controllers import nurses
app.register_blueprint(nurses)

from dev_log.patient.controllers import patients
app.register_blueprint(patients)

from dev_log.appointments.controllers import appointments
app.register_blueprint(appointments)

from dev_log.myaccount.controllers import account
app.register_blueprint(account)

db.create_all()

if not existing_database:
    from dev_log.init_database import init_db
    init_db()

# For CSS
app.static_folder = 'static'




