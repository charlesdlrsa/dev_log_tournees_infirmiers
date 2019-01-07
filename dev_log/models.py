from dev_log import db


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
        unique=True)

    nurse_id = db.Column(
        db.Integer,
        db.ForeignKey('nurse.nurse_id'),
        nullable=False,
        unique=True)

    care_id = db.Column(
        db.Integer,
        db.ForeignKey('care.care_id'),
        nullable=False,
        unique=True)

    date = db.Column(
        db.DateTime,
        nullable=False)

    def __init__(self, nurse_id, patient_id, date, care):
        self.__nurse_id = nurse_id
        self.__patient_id = patient_id
        self.__date = date
        self.__care = care


class Nurse(BasePerson):
    id = db.Column(
        'nurse_id',
        db.Integer,
        primary_key=True,
        nullable=False)

    password = db.Column(
        db.String(20),
        nullable=False)

    # competences = db.Column(db.String(50))

    appointments = db.relationship(
        'Appointment')

    office = db.relationship(
        'AssociationOfficeNurse')

    def __init__(self, last_name, first_name, email, password, phone,  address, office):
        self.__last_name = last_name
        self.__first_name = first_name
        self.__phone = phone
        self.__email = email
        self.__password = password
        self.__address = address
        self.__office = office
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

    def __init__(self, last_name, first_name, email, address, latitude, longitude, phone):
        self.__last_name = last_name
        self.__first_name = first_name
        self.__email = email
        self.__address = address
        self.__latitude = latitude
        self.__longitude = longitude
        self.__phone = phone


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

    def __init__(self, name, phone, adress):
        self.__name = name
        self.__phone = phone
        self.__address = adress


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
