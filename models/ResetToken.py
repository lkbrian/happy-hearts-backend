from config import db
from datetime import datetime,timedelta

class ResetToken(db.Model):
    __tablename__='resetokens'
    token_id= db.Column(db.Integer,primary_key=True)
    token = db.Column(db.String, nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=1))
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.parent_id"), nullable=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.provider_id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    parent = db.relationship("Parent", back_populates="reset_tokens")
    provider = db.relationship("Provider", back_populates="reset_tokens")
    user = db.relationship("User", back_populates="reset_tokens")
