from config import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import pytz

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class LabTest(db.Model, SerializerMixin):
    __tablename__ = "lab_tests"
    serialize_only = (
        "lab_test_id",
        "test_name",
        "test_date",
        "result",
        "remarks",
        "timestamp",
        "parent_id",
        "provider_id",
        "child_id",
        "parent.national_id",
        "child.certificate_No",
    )
    serialize_rules = ("-parent.lab_tests", "-child.lab_tests")
    lab_test_id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(255), nullable=False)
    test_date = db.Column(db.Date, nullable=False)
    result = db.Column(db.String(255), nullable=False)
    remarks = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    # Foreign key to either parent or child
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"), nullable=True)
    child_id = db.Column(db.Integer, db.ForeignKey("children.child_id"), nullable=True)
    provider_id = db.Column(
        db.Integer, db.ForeignKey("providers.provider_id"), nullable=True
    )

    parent = db.relationship("Parent", back_populates="lab_tests", lazy=True)
    child = db.relationship("Child", back_populates="lab_tests", lazy=True)
    provider = db.relationship("Provider", back_populates="lab_tests", lazy=True)
