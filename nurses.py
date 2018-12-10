from app import db


class Nurse(db.Model):
    id = db.Column('nurse_id', db.Integer, primary_key=True)
    last_name = db.Column(db.String(20))
    first_name = db.Column(db.String(20))
    email = db.Column(db.String(20))
    password = db.Column(db.String(20))
    address = db.Column(db.String(50))
    # competences = db.Column(db.String(50))

    def __init__(self, last_name, first_name, email, password, address):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.password = password
        self.address = address
        # self.competences = competences
