from config import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

import pytz

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class Provider(db.Model, SerializerMixin):
    __tablename__ = "providers"
    serialize_only = (
        "provider_id",
        "name",
        "email",
        "role",
        "national_id",
        "phone_number",
        "gender",
    )
    serialize_rules = (
        "-password_hash",
        "-appointments.provider",
        "-vaccination_records.provider",
        "-vaccination_records.child",
        "-prescriptions.provider",
        "-medications.provider",
        "-deliveries.provider",
        "-discharge_summaries.provider",
        "-admissions.provider",
        "-appointments.provider.info",
    )

    provider_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(70), nullable=False, unique=True)
    role = db.Column(db.String, default="provider", nullable=False)
    national_id = db.Column(db.Integer, unique=True, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False, unique=True)
    gender = db.Column(db.String, nullable=False)

    password_hash = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    deliveries = db.relationship(
        "Delivery", back_populates="provider", cascade="all, delete-orphan"
    )

    discharge_summaries = db.relationship(
        "Discharge_summary", back_populates="provider", cascade="all, delete-orphan"
    )
    admissions = db.relationship(
        "Admission", back_populates="provider", cascade="all, delete-orphan"
    )

    appointments = db.relationship(
        "Appointment", back_populates="provider", cascade="all, delete-orphan"
    )
    vaccination_records = db.relationship(
        "Record", back_populates="provider", cascade="all, delete-orphan"
    )

    medications = db.relationship(
        "Medications", back_populates="provider", cascade="all, delete-orphan"
    )
    lab_tests = db.relationship("LabTest", back_populates="provider", lazy=True)

    reset_tokens = db.relationship("ResetToken", back_populates="provider")
    prescriptions = db.relationship(
        "Prescription", back_populates="provider", lazy=True
    )
    documents = db.relationship("Document", back_populates="provider", lazy=True)
    discharge_summaries = db.relationship(
        "Discharge_summary", back_populates="provider"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
