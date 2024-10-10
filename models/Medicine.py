from config import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import json
from sqlalchemy.types import TypeDecorator, VARCHAR
import pytz

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


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


class Medicine(db.Model, SerializerMixin):
    __tablename__ = "medicines"
    serialize_only = (
        "medicine_id",
        "name",
        "composition",
        "dosage",
        "indication",
        "side_effects",
    )
    serialize_rules = (
        "-prescriptions.medicine",
    )  # Hide prescriptions from serialization if not needed

    medicine_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    composition = db.Column(db.String, nullable=False)
    dosage = db.Column(db.String, nullable=False)
    indication = db.Column(db.String, nullable=False)
    side_effects = db.Column(JSONEncodedList, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    # Relationships
    prescriptions = db.relationship(
        "Prescription", back_populates="medicine", lazy=True
    )
