from dev_log import db


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


class BasePerson(Base):
    __abstract__ = True
    last_name = db.Column(db.String(20))
    first_name = db.Column(db.String(20))
    email = db.Column(db.String(20))
    phone = db.Column(db.String(10))
    address = db.Column(db.String(50))


class Appointment(Base):
    id = db.Column('appointment_id', db.Integer, primary_key=True)
    nurse_id = db.Column(db.Integer)
    patient_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    care = db.Column(db.String(50))

    def __init__(self, nurse_id, patient_id, date, care):
        self.nurse_id = nurse_id
        self.patient_id = patient_id
        self.date = date
        self.care = care



class Nurse(BasePerson):
    id = db.Column('nurse_id', db.Integer, primary_key=True)
    password = db.Column(db.String(20))
    office = db.Column(db.ARRAY(db.Integer, as_tuple=False))
    # competences = db.Column(db.String(50))

    def __init__(self, last_name, first_name, email, password, address, office):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.password = password
        self.address = address
        self.office = office
        # self.competences = competences


class Patient(BasePerson):
    id = db.Column('patient_id', db.Integer, primary_key=True)
    related_office = db.Column(db.Integer)

    def __init__(self, last_name, first_name, email, address, related_office):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.address = address
        self.related_office = related_office

