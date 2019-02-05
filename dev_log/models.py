import googlemaps
from dev_log import db
from dev_log.key import key


class Base(db.Model):
    __abstract__ = True
    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False)

    def geolocation(self):
        """
        Set the attributes latitude and longitude of an address using Google Maps API.

        :param classe:
        :param key: Google Maps API key
        :return: latitude and
        """
        gmaps = googlemaps.Client(key=str(key))
        distance = gmaps.geocode(self.address)[0]['geometry']['location']
        self.latitude = distance['lat']
        self.longitude = distance['lng']


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


class Patient(BasePerson):
    id = db.Column(
        'patient_id',
        db.Integer,
        primary_key=True,
        nullable=False)

    digicode = db.Column(
        db.Integer)

    additional_postal_information = db.Column(
        db.String(50))

    latitude = db.Column(
        db.Float)

    longitude = db.Column(
        db.Float)

    office_id = db.Column(
        db.Integer,
        db.ForeignKey('office.office_id'),
        nullable=False)

    office = db.relationship(
        "Office",
        backref="office_patient")

    def __init__(self, last_name, first_name, email, address, phone, digicode,
                 additional_postal_information, office_id):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.address = address
        self.digicode = digicode
        self.additional_postal_information = additional_postal_information
        self.phone = phone
        self.office_id = office_id
        self.geolocation()


class Nurse(BasePerson):
    """
    Store the information of nurses.

    Attributes:
          office_id : id of the office the nurse works at.
          cares : string that contains the id of the cares the nurse can do.
    """
    id = db.Column(
        'nurse_id',
        db.Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True)

    password = db.Column(
        db.String(20),
        nullable=False)

    office_id = db.Column(
        db.Integer,
        db.ForeignKey('office.office_id'),
        nullable=False)

    cares = db.Column(
        db.String(50))

    office = db.relationship(
        "Office",
        backref="office_nurse")

    def __init__(self, last_name, first_name, email, password, phone,
                 address, office_id, cares):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.phone = phone
        self.password = password
        self.address = address
        self.office_id = office_id
        self.cares = cares


class Appointment(Base):
    """
    Store the information linked to an appointment request.

    Attributes:
          patient_id : id of the patient that needs an appointment.
          care_id : care requested by the patient.
          date, halfday : moment requested.
    """
    id = db.Column(
        'appointment_id',
        db.Integer,
        primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('patient.patient_id'),
        nullable=False,
        unique=False)

    care_id = db.Column(
        db.Integer,
        db.ForeignKey('care.care_id'),
        nullable=False,
        unique=False)

    date = db.Column(
        db.Date,
        nullable=False)

    halfday = db.Column(
        db.String)

    patient = db.relationship(
        "Patient",
        backref="patient")

    care = db.relationship(
        "Care",
        backref="care")

    def __init__(self, patient_id, date, care_id, halfday):
        self.patient_id = patient_id
        self.date = date
        self.halfday = halfday
        self.care_id = care_id


class Schedule(Base):
    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False)

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey('appointment.appointment_id'),
        unique=False)

    nurse_id = db.Column(
        db.Integer,
        db.ForeignKey('nurse.nurse_id'),
        unique=False)

    hour = db.Column(
        db.Time)

    appointment = db.relationship(
        "Appointment",
        backref="appointment")

    nurse = db.relationship(
        "Nurse",
        backref="nurse")

    def __init__(self, hour, nurse_id):
        self.hour = hour
        self.nurse_id = nurse_id


class Care(Base):
    """
    Store the cares provided by the nurses.

    Attributes:
        description : Description of the care.
        duration : Time (in minutes) needed to provide this care.
    """
    id = db.Column(
        'care_id',
        db.Integer,
        primary_key=True,
        nullable=False)

    description = db.Column(
        db.String(200))

    duration = db.Column(
        db.Integer,
        nullable=False)

    def __init__(self, description, duration):
        self.description = description
        self.duration = duration


class Office(Base):
    """
    Store the information of the offices.

    Attributes:
        name, phone address, email, password : Information of the office.
        latitude, longitude : Coordinates of the office, determined with geolocation function.
    """
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

    email = db.Column(
        db.String(20),
        nullable=False)

    password = db.Column(
        db.String(20),
        nullable=False)

    latitude = db.Column(
        db.Float)

    longitude = db.Column(
        db.Float)

    def __init__(self, name, address, email, phone, password):
        self.name = name
        self.address = address
        self.email = email
        self.phone = phone
        self.password = password
        self.geolocation()


class Absence(Base):
    """
        Store the absences by nurse, by date and halfday.

        Attributes:
              nurse_id : nurse that is absent
              date : date of absence.
              halfday : Morning or Afternoon.
        """
    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False)

    nurse_id = db.Column(
        db.Integer,
        db.ForeignKey('nurse.nurse_id'),
        unique=False)

    date = db.Column(
        db.Date,
        nullable=False)

    halfday = db.Column(
        db.String)

    nurse = db.relationship(
        "Nurse",
        backref="nurse_absence")

    def __init__(self, nurse_id, date, halfday):
        self.nurse_id = nurse_id
        self.date = date
        self.halfday = halfday
