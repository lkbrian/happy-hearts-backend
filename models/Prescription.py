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


class Prescription(db.Model, SerializerMixin):
    __tablename__ = "prescriptions"
    serialize_only = (
        "prescription_id",
        "parent_id",
        "provider_id",
        "child_id",
        "medicine_id",
        "quantity",
        "dosage",
        "duration",
        "refill_count",
        "filled_date",
        "expiry_date",
        "timestamp",
        "parent.name",
        "parent.national_id",
        "provider.name",
        "child.fullname",
        "child.certificate_No",
        "medicine.name",
    )
    serialize_rules = (
        "-parent.prescriptions",
        "-provider.prescriptions",
        "-child.prescriptions",
    )
    prescription_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("parents.parent_id"), nullable=True  # Nullable parent
    )
    provider_id = db.Column(
        db.Integer, db.ForeignKey("providers.provider_id"), nullable=False
    )
    child_id = db.Column(
        db.Integer, db.ForeignKey("children.child_id"), nullable=True  # Added child_id
    )
    medicine_id = db.Column(
        db.Integer, db.ForeignKey("medicines.medicine_id"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    dosage = db.Column(db.String, nullable=False)
    duration = db.Column(db.String, nullable=False)
    refill_count = db.Column(db.Integer, nullable=False, default=0)
    filled_date = db.Column(db.DateTime, nullable=True)
    expiry_date = db.Column(db.DateTime, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    # Relationships
    parent = db.relationship("Parent", back_populates="prescriptions", lazy=True)
    provider = db.relationship("Provider", back_populates="prescriptions", lazy=True)
    child = db.relationship("Child", back_populates="prescriptions", lazy=True)
    medicine = db.relationship(
        "Medicine", back_populates="prescriptions", lazy=True
    )  # Back-populate to Medicine
    medications = db.relationship(
        "Medications", back_populates="prescription", lazy=True
    )
