from config import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
import pytz

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class Appointment(db.Model, SerializerMixin):
    __tablename__ = "appointments"
    serialize_only = (
        "appointment_id",
        "appointment_date",
        "timestamp",
        "info",
        "reason",
        "status",  # Add status to serialized fields
    )
    serialize_rules = (
        "-parent.appointments",
        "-provider.appointments",
    )

    appointment_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("parents.parent_id"), nullable=False
    )
    provider_id = db.Column(
        db.Integer, db.ForeignKey("providers.provider_id"), nullable=False
    )
    reason = db.Column(db.String, nullable=False)

    appointment_date = db.Column(db.DateTime(timezone=True), nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=current_eat_time
    )
    
    status = db.Column(db.String, nullable=True, default="pending")

    parent = db.relationship("Parent", back_populates="appointments")
    provider = db.relationship("Provider", back_populates="appointments")

    @hybrid_property
    def info(self):
        return {
            "parent_name": self.parent.name,
            "provider_name": self.provider.name,
        }


