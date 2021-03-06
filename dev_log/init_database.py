import datetime
import random
from werkzeug.security import generate_password_hash
from dev_log.models import db, Nurse, Office, Patient, Care, Appointment, Schedule, Absence


def init_db():
    import logging as lg
    db.drop_all()
    db.create_all()
    password = generate_password_hash("password")
    db.session.add(Office(name="Massy", phone="0647859648", address="2 Rue Christophe Colomb, 91300 Massy",
                          email="massy@hotmail.fr", password=password))
    db.session.add(Office(name="Malakoff", phone="0609456784", address="27 Rue Alexis Martin, 92240 Malakoff",
                          email="malakoff@hotmail.fr", password=password))

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
    db.session.add(Nurse(last_name="Travers", first_name="Nicolas", email="nicolas.travers@hotmail.fr",
                         phone="0694697658", password=password, address="41 Rue Hévin, 92140 Clamart",
                         office_id=2, cares="-1-2-6-"))
    db.session.add(Nurse(last_name="Geraud", first_name="Rémi", email="remi.geraud@hotmail.fr",
                         phone="0694697468", password=password, address="16 rue Kléber, 92130 Issy-les-Moulineaux",
                         office_id=2, cares="-1-2-6-"))

    db.session.add(Patient(last_name="De la roche", first_name="Charles", email="charles.dlrsa@hotmail.fr",
                           address="40 rue Victor Hugo, 91300 Massy", phone="0699497758", digicode="6A78",
                           additional_postal_information="3eme gauche", office_id=1))
    db.session.add(Patient(last_name="Mallard", first_name="Alix", email="alix.mallard@hotmail.fr",
                           address="25 rue Pasteur, 91300 Massy", phone="0699265758", digicode="5A86",
                           additional_postal_information="RDC", office_id=1))
    db.session.add(Patient(last_name="Dieudonné", first_name="Maxime", email="maxime.dieudo@hotmail.fr",
                           address="79 rue Léonard de Vinci, 92160 Antony", phone="0649697758", digicode="2B81",
                           additional_postal_information="3eme gauche", office_id=1))
    db.session.add(Patient(last_name="Pascual", first_name="Romain", email="romain.pascual@hotmail.fr",
                           address="1 Rue du Canal, 91160 Longjumeau", phone="0678457127", digicode="4B34",
                           additional_postal_information="5eme gauche", office_id=1))
    db.session.add(Patient(last_name="Leveque", first_name="Hippolyte", email="hippolyte.leveque@hotmail.fr",
                           address="13 Rue Blaise Pascal, 91120 Palaiseau", phone="06746956667", digicode="4B34",
                           additional_postal_information="4eme droite", office_id=1))
    db.session.add(Patient(last_name="Cassedanne", first_name="Louis", email="louis.cassedanne@hotmail.fr",
                           address="20 Rue du Dr Roux, 91370 Verrières-le-Buisson", phone="0674695898",
                           digicode="1B12", additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Compain", first_name="Axel", email="axcompain@hotmail.fr",
                           address="1 Rue de la Forge, 91160 Longjumeau", phone="0624586941",
                           digicode="9C99", additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Lajouanie", first_name="Simon", email="simon.lajouanie@hotmail.fr",
                           address="12 Chemin du Paradis, 91430 Igny", phone="0674464466",
                           digicode="2D35", additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Martinet", first_name="Hugo", email="hugo.martinet@hotmail.fr",
                           address="21 Rue de la Chaudière, 91370 Verrières-le-Buisson", phone="0674316688",
                           digicode="7C58", additional_postal_information="4eme milieu", office_id=1))
    db.session.add(Patient(last_name="Béraud", first_name="Pauline", email="pauline.beraud@hotmail.fr",
                           address="35 Rue Jacques Duclos, 91120 Palaiseau", phone="0674697597",
                           digicode="4C36", additional_postal_information="7eme gauche", office_id=1))
    db.session.add(Patient(last_name="Taylor", first_name="Daniel", email="daniel.taylor@hotmail.fr",
                           address="36 rue Varengue, 92340 Bourg-la-Reine", phone="0674694623",
                           digicode="4C59", additional_postal_information="2eme gauche", office_id=1))
    db.session.add(Patient(last_name="Perez", first_name="Gael", email="gael.perez@hotmail.fr",
                           address="20 rue des Jacinthes, 94260 Fresnes", phone="0674694765",
                           digicode="3A45", additional_postal_information="1ere gauche", office_id=1))
    db.session.add(Patient(last_name="Mulciba", first_name="Mathis", email="mathis.mulciba@hotmail.fr",
                           address="26 rue Appert, 91300 Massy", phone="0674695898",
                           digicode="3A13", additional_postal_information="4eme gauche", office_id=1))
    db.session.add(Patient(last_name="Bureau", first_name="Baptiste", email="baptiste.bureau@hotmail.fr",
                           address="12 rue Albert Camus, 92160 Antony", phone="0674697611",
                           digicode="9C27", additional_postal_information="10eme gauche", office_id=1))
    db.session.add(Patient(last_name="Bellec", first_name="Thomas", email="thomas.bellec@hotmail.fr",
                           address="4 rue de Paris, 92190 Meudon", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=2))
    db.session.add(Patient(last_name="Thomas", first_name="Adrien", email="adrien.thomas@hotmail.fr",
                           address="20 rue Leriche, 75015 Paris", phone="0674695898", digicode="4B34",
                           additional_postal_information="2eme gauche", office_id=2))
    db.session.add(Patient(last_name="Borel", first_name="Edouard", email="edouard.borel@hotmail.fr",
                           address="29 rue d'Etienne d'Orves, 92120 Montrouge", phone="0674695898",
                           digicode="4B34", additional_postal_information="2eme gauche", office_id=2))

    db.session.add(Care(description="Bandage", duration=35))
    db.session.add(Care(description="Sting", duration=30))
    db.session.add(Care(description="Post operative", duration=20))
    db.session.add(Care(description="Injection", duration=35))
    db.session.add(Care(description="Auscultation", duration=20))
    db.session.add(Care(description="Assistance", duration=25))

    db.session.add(Absence(1, datetime.date(2019, 1, 10), "Afternoon"))
    db.session.add(Absence(2, datetime.date(2019, 2, 25), "Afternoon"))
    db.session.add(Absence(1, datetime.date(2019, 3, 10), "Morning"))
    db.session.add(Absence(2, datetime.date(2019, 4, 23), "Morning"))
    db.session.add(Absence(3, datetime.date(2019, 4, 23), "Morning"))
    db.session.add(Absence(4, datetime.date(2019, 4, 23), "Morning"))
    db.session.add(Absence(3, datetime.date(2019, 5, 2), "Morning"))
    db.session.add(Absence(4, datetime.date(2019, 5, 2), "Morning"))

    # to test the availabilities of the patient
    db.session.add(Appointment(patient_id=1, date=datetime.date(2019, 4, 26), care_id=random.randint(1, 6),
                               halfday="Afternoon"))

    # to test the availabilities of the nurses (solve_boolean)
    for pID in range(2, 10):
        db.session.add(Appointment(patient_id=pID, date=datetime.date(2019, 4, 23), care_id=random.randint(1, 6),
                                    halfday="Morning"))

    # to test the optimizer (solve_complete)
    for pID in range(1, 9):
        db.session.add(Appointment(patient_id=pID, date=datetime.date(2019, 5, 2), care_id=random.randint(1, 6),
                                   halfday="Morning"))
    db.session.commit()

    lg.warning('Database initialized!')
