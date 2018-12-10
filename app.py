from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configurations
app.config.from_object('config')

db = SQLAlchemy(app)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
