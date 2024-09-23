import os
import secrets
from datetime import datetime, timedelta
from venv import logger

from config import db, mail
from dotenv import load_dotenv
from flask import jsonify, make_response, request
from flask_mail import Message
from flask_restful import Resource
from models import Parent, Provider, ResetToken, User
from werkzeug.security import generate_password_hash

load_dotenv()


class ForgotPassword(Resource):

    def post(self):
        data = request.json
        email = data.get("email")

        if not email:
            return make_response(jsonify({"error": "Email is required"}), 400)

        # Check if the email belongs to a user, parent, or provider
        user = User.query.filter_by(email=email).first()
        parent = Parent.query.filter_by(email=email).first()
        provider = Provider.query.filter_by(email=email).first()

        if user:
            entity_id = user.user_id
            entity_type = "user"
        elif parent:
            entity_id = parent.parent_id
            entity_type = "parent"
        elif provider:
            entity_id = provider.provider_id
            entity_type = "provider"
        else:
            return make_response(
                jsonify({"error": "No account found with that email"}), 404
            )

        # Generate reset token
        reset_token = secrets.token_urlsafe(16)
        reset_token_entry = ResetToken(
            token=reset_token,
            expires_at=datetime.utcnow()
            + timedelta(hours=1),  # Token expires in 1 hour
        )

        # Associate reset token with the entity
        if entity_type == "user":
            reset_token_entry.user_id = entity_id
        elif entity_type == "parent":
            reset_token_entry.parent_id = entity_id
        elif entity_type == "provider":
            reset_token_entry.provider_id = entity_id

        db.session.add(reset_token_entry)
        db.session.commit()
        try:
            reset_link = f"http://localhost:4000/reset_password?token={reset_token}"

            # Plain text message
            text_body = f"Click the following link to reset your password: {reset_link}"

            # HTML message
            html_body = f"<p>Click the following link to reset your password:</p> <a href='{reset_link}'>{reset_link}</a>"

            msg = Message('Password Reset Request',
                sender=os.getenv('MAIL_USERNAME'),
                recipients=[email])

            # Set both plain text and HTML body
            msg.body = text_body
            msg.html = html_body

            mail.send(msg)

            return make_response(jsonify({'message': 'Password reset link sent to your email'}), 200)
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            db.session.rollback()
            return make_response(jsonify({'error': 'An error occurred while sending the email. Please try again later.'}), 500)


class ResetPassword(Resource):
    def post(self):
        data = request.json
        token = data.get("token")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        account_type = data.get("account_type")  # New field to identify account type

        # Validate inputs
        if not token:
            return make_response(jsonify({"msg": "Token is required"}), 400)
        if not new_password or not confirm_password:
            return make_response(jsonify({"msg": "Password fields are required"}), 400)
        if new_password != confirm_password:
            return make_response(jsonify({"msg": "Passwords do not match"}), 400)

        # Find the reset token entry
        reset_token_entry = ResetToken.query.filter_by(token=token).first()

        if not reset_token_entry:
            return make_response(jsonify({"msg": "Invalid or expired token"}), 400)

        # Check if the token is expired
        if reset_token_entry.expires_at < datetime.utcnow():
            db.session.delete(reset_token_entry)
            db.session.commit()
            return make_response(jsonify({"msg": "Token has expired"}), 400)

        # Determine which account type to reset based on account_type
        if account_type == "user":
            entity = User.query.filter_by(user_id=reset_token_entry.user_id).first()
        elif account_type == "parent":
            entity = Parent.query.filter_by(
                parent_id=reset_token_entry.parent_id
            ).first()
        elif account_type == "provider":
            entity = Provider.query.filter_by(
                provider_id=reset_token_entry.provider_id
            ).first()
        else:
            return make_response(jsonify({"msg": "Invalid account type"}), 400)

        # Ensure the entity exists
        if not entity:
            return make_response(
                jsonify({"msg": "No account associated with this token"}), 400
            )

        # Reset the password
        entity.password_hash = generate_password_hash(
            new_password
        )

        # Delete the reset token after use
        db.session.delete(reset_token_entry)
        db.session.commit()

        return make_response(
            jsonify({"msg": "Password has been reset successfully"}), 200
        )
