# custom_types.py
import json
from sqlalchemy.types import TypeDecorator, VARCHAR
from datetime import datetime
import pytz
from config import db 
from models import Appointment


def update_appointment_statuses():
    now = datetime.now(pytz.timezone("Africa/Nairobi"))
    check_date = datetime.strptime(now ,"%Y-%m-%d %H:%M")
    appointments = Appointment.query.filter(
        Appointment.appointment_date <= check_date, Appointment.status == "pending"
    ).all()

    for appointment in appointments:
        appointment.status = "missed"

    db.session.commit()


class JSONEncodedList(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return json.loads(value)
