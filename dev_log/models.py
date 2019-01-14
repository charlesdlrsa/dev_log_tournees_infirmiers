from dev_log import db
# import googlemaps
from werkzeug.security import check_password_hash, generate_password_hash

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

    latitude = db.Column(
        db.Float
    )

    longitude = db.Column(
        db.Float
    )

    def __init__(self, last_name, first_name, email, address, phone, latitude = None, longitude = None):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.address = address
        self.phone = phone
    #     Patient.geolocation(key)
    #
    # def geolocation(self, key):
    #     gmaps = googlemaps.Client(key=str(key))
    #     distance = gmaps.geocode(self.address)[0]['geometry']['location']
    #     self.latitude = distance['lat']
    #     self.longitude = distance['lng']


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

    office = db.Column(
        db.String(20),
        nullable=False)

    # competences = db.Column(db.String(50))

    def __init__(self, last_name, first_name, email, password,
                 phone, address, office, cares=None):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.phone = phone
        self.password = password
        self.address = address
        self.office = office
        # for care in cares:
        #     if care not in ["soin 1", "soin 2", "soin 3"]:
        #         raise ValueError("Unvalid care")
        self.cares = cares
        # self.competences = competences


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

    nurse_id = db.Column(
        db.Integer,
        db.ForeignKey('nurse.nurse_id'),
        unique=False)

    care_id = db.Column(
        db.Integer,
        db.ForeignKey('care.care_id'),
        nullable=False,
        unique=False)

    date = db.Column(
        db.Date,
        nullable=False)

    patient = db.relationship(
        "Patient",
        backref="patient")

    nurse = db.relationship(
        "Nurse",
        backref="nurse")

    care = db.relationship(
        "Care",
        backref="care")

    def __init__(self, nurse_id, patient_id, date, care_id):
        self.nurse_id = nurse_id
        self.patient_id = patient_id
        self.date = date
        self.care_id = care_id


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

    nurses = db.relationship("AssociationOfficeNurse")

    def __init__(self, name, address, email, phone, password):
        self.name = name
        self.address = address
        self.email = email
        self.phone = phone
        self.password = password


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


def init_db():
    import logging as lg
    db.drop_all()
    db.create_all()
    password = generate_password_hash("password")
    db.session.add(Office(name="Doctissimo", phone="0647859648", address="38 rue Lecourbe",
                          email="doctissimo@hotmail.fr", password=password))
    db.session.add(Nurse(last_name="Cabaret", first_name="Laurent", email="laurent.cabaret@hotmail.fr",
                         phone="0699458758", password=password, address="35 rue Bobigny", office="Paris"))
    db.session.add(Nurse(last_name="Poly", first_name="Jean-Philippe", email="jpp@hotmail.fr",
                         phone="0699458758", password=password, address="48 rue Clovis", office="Paris"))
    db.session.add(Nurse(last_name="Hulot", first_name="Celine", email="celine.hulot@hotmail.fr",
                         phone="0699469858", password=password, address="76 rue Paul André", office="Paris"))
    db.session.add(Nurse(last_name="Detriche", first_name="Jean-Marie", email="jeanmarie.detriche@hotmail.fr",
                         phone="0694699858", password=password, address="24 rue Terrence", office="Paris"))
    db.session.add(Patient(last_name="De la roche", first_name="Charles", email="charles.dlrsa@hotmail.fr",
                           address="40 rue Victor Hugo", phone="0699497758"))
    db.session.add(Patient(last_name="Mallard", first_name="Alix", email="alix.mallard@hotmail.fr",
                           address="25 rue Pasteur", phone="0699265758"))
    db.session.add(Patient(last_name="Dieudonné", first_name="Maxime", email="maxime.dieudo@hotmail.fr",
                           address="79 rue Vinci", phone="0649697758"))
    db.session.add(Patient(last_name="Pascual", first_name="Romain", email="romain.pascual@hotmail.fr",
                           address="178 rue Sadi Carnot", phone="0678697758"))
    db.session.add(Patient(last_name="Leveque", first_name="Hippolyte", email="hippolyte.leveque@hotmail.fr",
                           address="41 rue Boulard", phone="0674697758"))
    db.session.add(Patient(last_name="Cassedanne", first_name="Louis", email="louis.cassedanne@hotmail.fr",
                           address="325 rue Lecourbe", phone="0674695898"))
    db.session.add(Care(description="Pansement", duration=60))
    db.session.add(Care(description="Piqûre", duration=60))
    db.session.add(Care(description="Post opératoire", duration=60))
    db.session.commit()
    lg.warning('Database initialized!')
