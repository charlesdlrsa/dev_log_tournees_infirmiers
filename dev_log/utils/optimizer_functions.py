from flask import session
from dev_log.models import Appointment, Patient, Nurse, Care, Office


def build_data_for_optimizer(date, halfday, care_id=None, patient_id=None):
    """ A function that put in form the data for the optimizer """
    if session.get('office_id'):
        office_id = session['office_id']
    else:
        office_id = session['nurse_office_id']
    nurses_office = Nurse.query.filter(Nurse.office_id == office_id).all()
    nurses_absent = Nurse.query.filter(Nurse.nurse_absence.any(date=date),
                                       Nurse.office_id == office_id).all()
    nurses = list(set(nurses_office) - set(nurses_absent))
    office = Office.query.filter(Office.id == office_id).first()

    data = {}
    data["nurse_id"] = [str(nurse.id) for nurse in nurses]
    data["office_lat"] = str(office.latitude)
    data["office_lon"] = str(office.longitude)
    if halfday == "Morning":
        data["start"] = "08:00"
        data["end"] = "12:00"
    if halfday == "Afternoon":
        data["start"] = "14:00"
        data["end"] = "18:00"

    appointments = Appointment.query.filter(Appointment.date == date,
                                            Appointment.halfday == halfday,
                                            Appointment.patient.has(office_id=office_id)).all()
    data["appointments"] = []
    for app in appointments:
        app_data = {}
        app_data["app_id"] = str(app.id)
        app_data["app_lat"] = str(app.patient.latitude)
        app_data["app_lon"] = str(app.patient.longitude)
        app_data["app_length"] = str(app.care.duration)
        data["appointments"].append(app_data)
    if patient_id is not None:
        patient = Patient.query.filter(Patient.id == patient_id).first()
        care = Care.query.filter(Care.id == care_id).first()
        new_app_data = {}
        new_app_data["app_id"] = "1000000"
        new_app_data["app_lat"] = str(patient.latitude)
        new_app_data["app_lon"] = str(patient.longitude)
        new_app_data["app_length"] = str(care.duration)
        data["appointments"].append(new_app_data)

    return data
