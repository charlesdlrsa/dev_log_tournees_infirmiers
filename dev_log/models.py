from dev_log import db

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


class Appointment(Base):
    id = db.Column('appointment_id', db.Integer, primary_key=True)
    nurse_id = db.Column(db.Integer)
    patient_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    care = db.Column(db.String(50))

    def __init__(self, nurse_id, patient_id, date, care):
        self.__nurse_id = nurse_id
        self.__patient_id = patient_id
        self.__date = date
        self.__care = care


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


class Patient(Base):
    id = db.Column('patient_id', db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    mail = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)

    def __init__(self, id, name, mail, phone):
        self.__id = id
        self.__name = name
        self.__mail = mail
        self.__phone = phone
