from pkg_resources import get_distribution, DistributionNotFound

# The right way of setting project version
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Config options
app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']

# Create database connection object
db = SQLAlchemy(app)

from dev_log.auth.controllers import auth

app.register_blueprint(auth)

db.create_all()

# For CSS
app.static_folder = 'static'
