from flask import request, render_template
from appointments import Appointment
from app import db


class AppointmentController:

    @app.route('/', methods=["GET", "POST"])
    def home():
        appointments = None
        if request.form:
            try:
                appointment = Appointment(request.form.get("nurse"),
                                          request.form.get("patient"),
                                          request.form.get("date"),
                                          request.form.get("care"))
                db.session.add(appointment)
                db.session.commit()
            except Exception as e:
                print("Failed to add appointment")
                print(e)
        appointments = Appointment.query.all()
        return render_template("home.html", appointments=appointments)

    @app.route("/update", methods=["POST"])
    def update():
        try:
            newtitle = request.form.get("newtitle")
            oldtitle = request.form.get("oldtitle")
            appointment = Appointment.query.filter_by(title=oldtitle).first()
            appointment.title = newtitle
            db.session.commit()
        except Exception as e:
            print("Couldn't update appointment")
            print(e)
        return redirect("/")

