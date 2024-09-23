from sqlalchemy import Enum
from config import db, valid_roles
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pytz

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    serialize_only = (
        "user_id",
        "name",
        "email",
        "role",
        "timestamp",
    )

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(70), nullable=False, unique=True)
    role = db.Column(
        Enum(*valid_roles),
        nullable=False,
    )
    password_hash = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    reset_tokens = db.relationship("ResetToken", back_populates="user")

    __mapper_args__ = {"polymorphic_on": role}

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Admin(User):
    __mapper_args__ = {"polymorphic_identity": "admin"}


class ReceptionDesk(User):
    __mapper_args__ = {"polymorphic_identity": "reception_desk"}


class AccountsDesk(User):
    __mapper_args__ = {"polymorphic_identity": "accounts_desk"}


class Accounts(User):
    __mapper_args__ = {"polymorphic_identity": "accounts"}
