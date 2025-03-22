from config import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import pytz

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class Payment(db.Model, SerializerMixin):
    __tablename__ = "payments"
    serialize_only = (
        "payment_id",
        "parent_id",
        "amount",
        "payment_method",
        "timestamp",
    )

    serialize_rules = ("-parent.payments",)
    payment_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.String, db.ForeignKey("parents.parent_id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    parent = db.relationship("Parent", back_populates="payments")
