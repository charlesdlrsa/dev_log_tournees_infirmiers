from flask import session
from dev_log.models import Appointment, Patient, Nurse, Care, Office


def build_data_for_optimizer(date, halfday, care_id=None, new_appointment=None):
    """ A function that put in form the data for the optimizer """

    nurses_office = Nurse.query.filter(Nurse.office_id == session['office_id']).all()
    nurses_absent = Nurse.query.filter(Nurse.nurse_absence.any(date=date)).all()
    nurses = list(set(nurses_office) - set(nurses_absent))
    office = Office.query.filter(Office.id == session['office_id']).first()
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

    appointments = Appointment.query.filter(Appointment.date == date, Appointment.halfday == halfday).all()
    data["appointments"] = []
    for app in appointments:
        app_data = {}
        app_data["app_id"] = str(app.id)
        app_data["app_lat"] = str(app.patient.latitude)
        app_data["app_lon"] = str(app.patient.longitude)
        app_data["app_length"] = str(app.care.duration)
        data["appointments"].append(app_data)
    if new_appointment is not None:
        new_app_data = {}
        new_app_data["app_id"] = str(new_appointment.id)
        new_app_data["app_lat"] = str(new_appointment.patient.latitude)
        new_app_data["app_lon"] = str(new_appointment.patient.longitude)
        new_app_data["app_length"] = str(new_appointment.care.duration)
        data["appointments"].append(new_app_data)

    return data
