from app import db


class Appointment(db.Model):
    nurse_id = db.Column(db.Integer)
    patient_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    care = db.Column(db.String(50))

    def __init__(self, nurse_id, patient_id, date, care):
        self.__nurse_id = nurse_id
        self.__patient_id = patient_id
        self.__date = date
        self.__care = care

