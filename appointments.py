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

    @property
    def nurse_id(self):
        return self.__nurse_id

    @nurse_id.setter
    def nurse_id(self, id):
        self.__nurse_id = id

    @property
    def patient_id(self):
        return self.__patient_id

    @patient_id.setter
    def patient_id(self, id):
        self.__patient_id = id

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, date):
        self.__date = date

    @property
    def care(self):
        return self.__care

    @care.setter
    def care(self, care):
        self.__care = care



