import googlemaps
from werkzeug.security import check_password_hash, generate_password_hash
from dev_log import db
from dev_log.key import key
import datetime
import random


def geolocation(classe, key):
    gmaps = googlemaps.Client(key=str(key))
    distance = gmaps.geocode(classe.address)[0]['geometry']['location']
    classe.latitude = distance['lat']
    classe.longitude = distance['lng']


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
        db.Float
    )

    longitude = db.Column(
        db.Float
    )

    office_id = db.Column(
        db.Integer,
        db.ForeignKey('office.office_id'),
        nullable=False)

    office = db.relationship(
        "Office",
        backref="office_patient")

    def __init__(self, last_name, first_name, email, address, phone, digicode, additional_postal_information,
                 office_id, latitude=None, longitude=None):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.address = address
        self.digicode = digicode
        self.additional_postal_information = additional_postal_information
        self.phone = phone
        self.office_id = office_id
        geolocation(self, key)


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

    office_id = db.Column(
        db.Integer,
        db.ForeignKey('office.office_id'),
        nullable=False)

    cares = db.Column(
        db.String(50)
    )

    office = db.relationship(
        "Office",
        backref="office_nurse")

    def __init__(self, last_name, first_name, email, password, phone, address, office_id, cares):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.phone = phone
        self.password = password
        self.address = address
        self.office_id = office_id
        self.cares = cares


class Appointment(Base):
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
        db.String
    )

    patient = db.relationship(
        "Patient",
        backref="patient")

    care = db.relationship(
        "Care",
        backref="care")

    def __init__(self, patient_id, date, care_id, halfday=None):
        self.patient_id = patient_id
        self.date = date
        self.halfday = halfday
        self.care_id = care_id


class Schedule(Base):
    id = db.Column(
        'appointment_id',
        db.Integer,
        primary_key=True,
        nullable=False
    )

    nurse_id = db.Column(
        db.Integer,
        db.ForeignKey('nurse.nurse_id'),
        unique=False)

    hour = db.Column(
        db.Time
    )

    # appointment = db.relationship(
    #     "Appointment",
    #     backref="appointment"
    # )

    nurse = db.relationship(
        "Nurse",
        backref="nurse")

    def __init__(self, hour, nurse_id):
        self.hour = hour
        self.nurse_id = nurse_id


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

    def __init__(self, description, duration):
        self.description = description
        self.duration = duration


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

    email = db.Column(
        db.String(20),
        nullable=False)

    password = db.Column(
        db.String(20),
        nullable=False)

    latitude = db.Column(
        db.Float
    )

    longitude = db.Column(
        db.Float
    )

    nurses = db.relationship("AssociationOfficeNurse")

    def __init__(self, name, address, email, phone, password, latitude=None, longitude=None):
        self.name = name
        self.address = address
        self.email = email
        self.phone = phone
        self.password = password
        geolocation(self, key)


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


class Absence(Base):
    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False
    )

    nurse_id = db.Column(
        db.Integer,
        db.ForeignKey('nurse.nurse_id'),
        unique=False)

    date = db.Column(
        db.Date,
        nullable=False)

    halfday = db.Column(
        db.String
    )

    nurse = db.relationship(
        "Nurse",
        backref="nurse_absence")

    def __init__(self, nurse_id, date, halfday):
        self.nurse_id = nurse_id
        self.date = date
        self.halfday = halfday


def init_db():
    import logging as lg
    db.drop_all()
    db.create_all()
    password = generate_password_hash("password")
    db.session.add(Office(name="Doctissimo", phone="0647859648", address="2 Rue Christophe Colomb, 91300 Massy",
                          email="doctissimo@hotmail.fr", password=password))
    db.session.add(Nurse(last_name="Cabaret", first_name="Laurent", email="laurent.cabaret@hotmail.fr",
                         phone="0699458758", password=password, address="25 rue de la Ferronerie, 91430 Igny",
                         office_id=1, cares="-1-3-4-"))
    db.session.add(Nurse(last_name="Poli", first_name="Jean-Philippe", email="jpp@hotmail.fr",
                         phone="0699458758", password=password,
                         address="2 rue de la Vieille Poste, 78350 Jouy-en-Josas",
                         office_id=1, cares="-1-2-5-"))
    db.session.add(Nurse(last_name="Hudelot", first_name="Celine", email="celine.hudelot@hotmail.fr",
                         phone="0699469858", password=password, address="20 rue de la Villacoublay, 78140 Vélizy",
                         office_id=1, cares="-3-5-6-"))
    db.session.add(Nurse(last_name="Detriche", first_name="Jean-Marie", email="jeanmarie.detriche@hotmail.fr",
                         phone="0694699858", password=password, address="45 avenue Saint Laurent, 91400 Orsay",
                         office_id=1, cares="-1-2-6-"))
    db.session.add(Patient(last_name="De la roche", first_name="Charles", email="charles.dlrsa@hotmail.fr",
                           address="40 rue Victor Hugo 91300 Massy", phone="0699497758", digicode="4B34",
                           additional_postal_information="3eme gauche", office_id=1))
    db.session.add(Patient(last_name="Mallard", first_name="Alix", email="alix.mallard@hotmail.fr",
                           address="25 rue Pasteur 91300 Massy", phone="0699265758", digicode="4B34",
                           additional_postal_information="RDC", office_id=1))
    db.session.add(Patient(last_name="Dieudonné", first_name="Maxime", email="maxime.dieudo@hotmail.fr",
                           address="79 rue Léonard de Vinci 92160 Antony", phone="0649697758", digicode="4B34",
                           additional_postal_information="3eme gauche", office_id=1))
    db.session.add(Patient(last_name="Pascual", first_name="Romain", email="romain.pascual@hotmail.fr",
                           address="1 Rue du Canal, 91160 Longjumeau", phone="0678697758", digicode="4B34",
                           additional_postal_information="5eme gauche", office_id=1))
    db.session.add(Patient(last_name="Leveque", first_name="Hippolyte", email="hippolyte.leveque@hotmail.fr",
                           address="13 Rue Blaise Pascal, 91120 Palaiseau", phone="0674697758", digicode="4B34",
                           additional_postal_information="4eme droite", office_id=1))
    db.session.add(Patient(last_name="Cassedanne", first_name="Louis", email="louis.cassedanne@hotmail.fr",
                           address="20 Rue du Dr Roux 91370 Verrières-le-Buisson", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Compain", first_name="Axel", email="axcompain@hotmail.fr",
                           address="5 avenue Victor Hugo, 92170 Vanves", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Lajouanie", first_name="Simon", email="simon.lajouanie@hotmail.fr",
                           address="39 rue du Général Leclerc, 92130 Issy Les Moulineaux", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Bellec", first_name="Thomas", email="thomas.bellec@hotmail.fr",
                           address="4 rue de Paris, 92190 Meudon", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Thomas", first_name="Adrien", email="adrien.thomas@hotmail.fr",
                           address="20 rue Leriche, 75015 Paris", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Borel", first_name="Edouard", email="edouard.borel@hotmail.fr",
                           address="29 rue d'Etienne d'Orves, 92120 Montrouge", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Martinet", first_name="Hugo", email="hugo.martinet@hotmail.fr",
                           address="79 Avenue du Président Allende, 94800 Villejuif", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Taylor", first_name="Daniel", email="daniel.taylor@hotmail.fr",
                           address="36 rue Varengue, 92340 Bourg-la-Reine", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Care(description="Bandage", duration=60))
    db.session.add(Care(description="Sting", duration=30))
    db.session.add(Care(description="Post operative follow-up", duration=20))
    db.session.add(Care(description="Injection", duration=35))
    db.session.add(Care(description="Auscultation", duration=20))
    db.session.add(Care(description="Assistance", duration=60))
    halfday = ["Morning", "Afternoon"]
    for pID in range(1, 7):
        db.session.add(Appointment(patient_id=pID, date=datetime.date(2019, 5, 5), care_id=random.randint(1, 3),
                                   halfday=halfday[pID % 2]))
        db.session.add(Schedule(hour=datetime.time(8 + pID % 2 * 6 + pID - 1), nurse_id=random.randint(1, 4)))
    db.session.commit()
    lg.warning('Database initialized!')
