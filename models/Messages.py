from datetime import datetime
import pytz
from sqlalchemy_serializer import SerializerMixin
from config import db

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class Message(db.Model, SerializerMixin):
    __tablename__ = "messages"
    serialize_only = (
        "message_id",
        "first_name",
        "last_name",
        "email",
        "message",
        "user_id",
        "parent_id",
        "provider_id",
        "conversation_id",
        "timestamp",
    )

    message_id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("conversations.conversation_id"), nullable=False
    )
    first_name = db.Column(db.String, nullable=True)  # Nullable for guests
    last_name = db.Column(db.String, nullable=True)  # Nullable for guests
    email = db.Column(db.String, nullable=True)  # Nullable for guests
    message = db.Column(db.Text, nullable=False)

    # Foreign keys for relationships
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # Nullable for guests
    parent_id = db.Column(
        db.Integer, db.ForeignKey("parents.parent_id"), nullable=True
    )  # Nullable for guests
    provider_id = db.Column(
        db.Integer, db.ForeignKey("providers.provider_id"), nullable=True
    )  # Nullable for guests

    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)

    # Relationships
    user = db.relationship("User", back_populates="messages", lazy=True)
    parent = db.relationship("Parent", back_populates="messages", lazy=True)
    provider = db.relationship("Provider", back_populates="messages", lazy=True)
    conversation = db.relationship("Conversation", back_populates="messages", lazy=True)


class Conversation(db.Model):
    __tablename__ = "conversations"

    conversation_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=current_eat_time)

    # Establishing a relationship to messages
    messages = db.relationship("Message", back_populates="conversation", lazy=True)
