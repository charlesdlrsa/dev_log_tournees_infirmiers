DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Define the application directory
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains Cross-site Request Forgery (CSRF)
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

# To generate a new secret key:
# import random, string
# "".join([random.choice(string.printable) for _ in range(24)])
SECRET_KEY = 'dVys\n8D%M{o{&Tr3n*f2l3@\r'

APP_ID = 1200420960103822
