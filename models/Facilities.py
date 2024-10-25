from datetime import datetime

import pytz

# from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class Bed(db.Model, SerializerMixin):
    __tablename__ = "beds"

    serialize_only = (
        "bed_id",
        "bed_number",
        "is_occupied",
        "room_id",
        "bed_type",
        "room.room_number",
    )
    serialize_rules = ("-room.beds", "-admission.bed")

    bed_id = db.Column(db.Integer, primary_key=True)
    bed_number = db.Column(db.String, nullable=False, unique=True)
    bed_type = db.Column(db.String, nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.room_id"), nullable=False)

    room = db.relationship("Room", back_populates="beds")
    admission = db.relationship("Admission", back_populates="bed", uselist=False)


class Room(db.Model, SerializerMixin):
    __tablename__ = "rooms"

    serialize_only = (
        "room_id",
        "room_number",
        "is_occupied",
        "room_type",
        "status",
        "location",
        "facilities",
        "notes",
    )
    serialize_rules = ("-admissions.room",)

    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String, unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_occupancy = db.Column(db.Integer, default=0)
    current_bed_occupancy = db.Column(db.Integer, default=0)
    room_type = db.Column(db.String, nullable=False)
    facilities = db.Column(db.String)
    location = db.Column(db.String)
    status = db.Column(db.String, default="Available")
    notes = db.Column(db.Text)
    is_occupied = db.Column(db.Boolean, default=False)

    admissions = db.relationship(
        "Admission", back_populates="room", cascade="all, delete-orphan"
    )
    beds = db.relationship("Bed", back_populates="room", cascade="all, delete-orphan")
