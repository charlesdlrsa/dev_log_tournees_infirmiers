from dev_log import db

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


class Appointment(Base):
    id = db.Column('appointment_id', db.Integer, primary_key=True)
    patient_id = db.Column(
            db.Integer, 
            db.ForeignKey('patient.id'), 
            nullable=False, 
            unique=True)

    nurse_id = db.Column(
        db.Integer, 
        db.ForeignKey('nurse.nurse_id'), 
        nullable=False)

    date = db.Column(db.DateTime, nullable=False)
    care_id = db.Column(
            db.Integer, 
            db.ForeignKey('care.care_id'), 
            nullable=False, 
            unique=True)

    def __init__(self, nurse_id, patient_id, date, care):
        self.__nurse_id = nurse_id
        self.__patient_id = patient_id
        self.__date = date
        self.__care = care

    # @property
    # def nurse_id(self):
    #     return self.__nurse_id
    #
    # @nurse_id.setter
    # def nurse_id(self, id):
    #     self.__nurse_id = id
    #
    # @property
    # def patient_id(self):
    #     return self.__patient_id
    #
    # @patient_id.setter
    # def patient_id(self, id):
    #     self.__patient_id = id
    #
    # @property
    # def date(self):
    #     return self.__date
    #
    # @date.setter
    # def date(self, date):
    #     self.__date = date
    #
    # @property
    # def care(self):
    #     return self.__care
    #
    # @care.setter
    # def care(self, care):
    #     self.__care = care


class Nurse(Base):
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

class Care(Base):
    id = db.Column('care_id', db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    duration = db.Column(db.Integer) # duration in minutes

    def __init__(self, description, duration):
        self.description = description
        self.duration = duration