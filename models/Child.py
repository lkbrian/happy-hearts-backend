from datetime import datetime

import pytz

# from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class Child(db.Model, SerializerMixin):
    __tablename__ = "children"
    serialize_only = (
        "child_id",
        "fullname",
        "certificate_No",
        "date_of_birth",
        "age",
        "gender",
        "prescriptions",
    )
    serialize_rules = (
        "-parent_id",
        "-prescriptions.child",
        "-records.child",
        "-lab_tests.child",
        "-discharge_summaries.child",
        "-admissions.child",
        "-medications.child",
        "-prescriptions.child",
    )
    child_id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String, nullable=False)
    certificate_No = db.Column(db.Integer, unique=True, nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    age = db.Column(db.String, nullable=True)
    gender = db.Column(db.String, nullable=False)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("parents.parent_id"), nullable=False
    )

    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)
    discharge_summaries = db.relationship(
        "Discharge_summary", back_populates="child", cascade="all, delete-orphan"
    )
    admissions = db.relationship(
        "Admission", back_populates="child", cascade="all, delete-orphan"
    )
    parent = db.relationship("Parent", back_populates="children")
    lab_tests = db.relationship(
        "LabTest", back_populates="child", cascade="all, delete-orphan", lazy=True
    )
    records = db.relationship(
        "Record", back_populates="child", lazy=True, cascade="all, delete-orphan"
    )
    prescriptions = db.relationship(
        "Prescription", back_populates="child", lazy=True, cascade="all, delete-orphan"
    )
    medications = db.relationship(
        "Medications", back_populates="child", lazy=True, cascade="all, delete-orphan"
    )


class Record(db.Model, SerializerMixin):
    __tablename__ = "vacination_records"
    serialize_only = (
        "record_id",
        "parent_id",
        "vaccine_id",
        "provider_id",
        "child_id",
        "timestamp",
        # "info",
    )
    serialize_rules = (
        "-vaccine",
        "-child",
        "-provider",
    )
    record_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("parents.parent_id"), nullable=False
    )
    vaccine_id = db.Column(
        db.Integer, db.ForeignKey("vaccines.vaccine_id"), nullable=False
    )
    provider_id = db.Column(
        db.String, db.ForeignKey("providers.provider_id"), nullable=False
    )
    child_id = db.Column(db.Integer, db.ForeignKey("children.child_id"), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    parent = db.relationship("Parent", back_populates="vaccination_records")
    vaccine = db.relationship("Vaccine", back_populates="vaccination_records")
    provider = db.relationship("Provider", back_populates="vaccination_records")
    child = db.relationship("Child", back_populates="records")
