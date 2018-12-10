import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import auth


app = Flask(__name__)
app.config.from_object('config')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

app.register_blueprint(auth.bp)

db.create_all()
app.run()
