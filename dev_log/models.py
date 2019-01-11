from dev_log import db
from sqlalchemy.sql import select


class Base(db.Model):
    __abstract__ = True
    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False)


class BasePerson(Base):
    __abstract__ = True

    last_name = db.Column(
        db.String(20),
        nullable=False)

    first_name = db.Column(
        db.String(20),
        nullable=False)

    email = db.Column(
        db.String(20),
        nullable=False)

    phone = db.Column(
        db.String(10),
        nullable=False)

    address = db.Column(
        db.String(50),
        nullable=False)


class Appointment(Base):
    id = db.Column('appointment_id', db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('patient.patient_id'),
        nullable=False,
        unique=False)

    nurse_id = db.Column(
        db.Integer,
        db.ForeignKey('nurse.nurse_id'),
        nullable=False,
        unique=False)

    care_id = db.Column(
        db.Integer,
        db.ForeignKey('care.care_id'),
        nullable=False,
        unique=False)

    date = db.Column(
        db.DateTime,
        nullable=False)

    def __init__(self, nurse_id, patient_id, date, care_id):
        self.nurse_id = nurse_id
        self.patient_id = patient_id
        self.date = date
        self.care_id = care_id
        self.patient_name = Patient.query.with_entities(Patient.last_name)\
            .filter(Patient.id == self.patient_id).first()


class Nurse(BasePerson):
    id = db.Column(
        'nurse_id',
        db.Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True)

    password = db.Column(
        db.String(20),
        nullable=False)

    appointments = db.relationship(
        'Appointment')

    office = db.Column(
        db.String(20),
        nullable=False)

    # office = db.relationship(
    #     'AssociationOfficeNurse')

    # competences = db.Column(db.String(50))

    def __init__(self, last_name, first_name, email, password, phone,  address, office):
        self.last_name = last_name
        self.first_name = first_name
        self.phone = phone
        self.email = email
        self.password = password
        self.address = address
        self.office = office
        # self.competences = competences


class Care(Base):
    id = db.Column(
        'care_id',
        db.Integer,
        primary_key=True,
        nullable=False)

    description = db.Column(
        db.String(200))

    duration = db.Column(  # duration in minutes
        db.Integer,
        nullable=False)

    appointments = db.relationship(
        'Appointment')

    def __init__(self, description, duration):
        self.__description = description
        self.__duration = duration


class Patient(BasePerson):
    id = db.Column(
        'patient_id',
        db.Integer,
        primary_key=True,
        nullable=False)

    appointments = db.relationship(
        'Appointment')

    def __init__(self, last_name, first_name, email, address,phone):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.address = address
        self.latitude = None
        self.longitude = None
        self.phone = phone


class Office(Base):
    id = db.Column(
        'office_id',
        db.Integer,
        primary_key=True,
        nullable=False)

    name = db.Column(
        db.String(50),
        nullable=False)

    phone = db.Column(
        db.String(10),
        nullable=False)

    address = db.Column(
        db.String(50),
        nullable=False)

    nurses = db.relationship("AssociationOfficeNurse")

    def __init__(self, name, phone, address):
        self.__name = name
        self.__phone = phone
        self.__address = address


# Many to Many relation
class AssociationOfficeNurse(Base):
    office_id = db.Column(
        db.Integer,
        db.ForeignKey('office.office_id'),
        primary_key=True,
        nullable=False)

    nurse_id = db.Column(
        db.Integer,
        db.ForeignKey('nurse.nurse_id'),
        primary_key=True,
        nullable=False)

    nurse = db.relationship("Nurse")

    office = db.relationship("Office")
