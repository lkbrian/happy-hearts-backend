from config import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
import pytz

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class Document(db.Model, SerializerMixin):
    __tablename__ = "documents"
    serialize_only = (
        "document_id",
        "entityType",
        "documentType",
        "fileName",
        "url",
        "parent_id",
        "provider_id",
        "child_id",
        "timestamp",
    )
    document_id = db.Column(db.Integer, primary_key=True)
    entityType = db.Column(db.String, nullable=False)
    documentType = db.Column(db.String, nullable=False)
    fileName = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String, nullable=False)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("parents.parent_id"), nullable=True  # Nullable parent
    )
    provider_id = db.Column(
        db.Integer, db.ForeignKey("providers.provider_id"), nullable=True
    )
    child_id = db.Column(db.Integer, db.ForeignKey("children.child_id"), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=current_eat_time)
    parent = db.relationship("Parent", back_populates="documents", lazy=True)

    # Relationship with Provider
    provider = db.relationship("Provider", back_populates="documents", lazy=True)
