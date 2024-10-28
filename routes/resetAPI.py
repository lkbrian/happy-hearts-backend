import email
import os
import secrets
from datetime import datetime, timedelta
from sqlite3 import IntegrityError
from venv import logger

from config import db, mail
from dotenv import load_dotenv
from flask import jsonify, make_response, request
from flask_mail import Message
from flask_restful import Resource
from models import Parent, Provider, ResetToken, User
from werkzeug.security import generate_password_hash
import random

load_dotenv()


class ForgotPassword(Resource):

    def post(self):
        data = request.json
        email = data.get("email")
        account_type = data.get("account_type")

        if not email:
            return make_response(jsonify({"error": "Email is required"}), 400)

        if account_type == "user":
            user = User.query.filter_by(email=email).first()
            if user:
                entity_id = user.user_id
                entity_type = "user"
            else:
                return make_response(
                    jsonify({"error": "No user found with that email"}), 404
                )

        elif account_type == "parent":
            parent = Parent.query.filter_by(email=email).first()
            if parent:
                entity_id = parent.parent_id
                entity_type = "parent"
            else:
                return make_response(
                    jsonify({"error": "No parent found with that email"}), 404
                )

        elif account_type == "provider":
            provider = Provider.query.filter_by(email=email).first()
            if provider:
                entity_id = provider.provider_id
                entity_type = "provider"
            else:
                return make_response(
                    jsonify({"error": "No provider found with that email"}), 404
                )

        else:
            return make_response(jsonify({"msg": "Invalid account type"}), 400)

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
            expiration_time = "1 hour"

            html_body = f"""
            <div
              style="width: 100%;background: #ebf2fa;padding: 20px 0 0 0;font-family: system-ui, sans-serif; text-align: center;">
              <div
              style="border-top: 6px solid #007BFF; background-color: #fff; display: block; padding:  8px 20px; text-align: center;   max-width: 500px;  border-bottom-left-radius: .4rem; border-bottom-right-radius: .4rem; letter-spacing: .037rem; line-height: 26px;  margin: auto; font-size: 14px; ">
              <!-- Logo -->
              <img src="https://res.cloudinary.com/droynil1n/image/upload/v1728204000/e50iplialg1fawi16enn.png"
                  alt="Happy Hearts Logo" style="width: 70%; height: auto; margin:auto">
              <!-- Content Section -->
              <div style="text-align: left; padding-top: 10px;">
                  <p>We've received a request to reset the password for the Happy Hearts account associated with {email}.
                  Please note that no changes have been made to your account yet. We recommend resetting your password
                  immediately
                  to ensure the security of your account.</p>
                  <p>Click the button below to reset your password:</p>
              </div>
              <!-- Button -->
              <a href='{reset_link}'
                  style='display: inline-block;width:90%; padding: 8px 20px;  color: white; background: linear-gradient(to bottom right, rgba(33,121,243,1) 25%, rgba(65,202,227,1) 100%); text-decoration: none; border-radius: .4rem;'>
                  Reset Password
              </a>
              <!-- Additional Information -->
              <div style="text-align: center; padding-top: 2px;">
                  <p>This link will expire in <strong>{expiration_time}</strong>.</p>
                  <p> For assistance, reach us at
                  <a href='mailto:{os.getenv(' MAIL_USERNAME')}'
                      style='color: #007BFF; text-decoration: underline;'>{os.getenv('MAIL_USERNAME')}</a>.
                  </p>
              </div>
              </div>
              <p style="padding: 20px 0 5px 0; text-align: center;color: rgb(150, 150, 150);font-size: 12px;">Happy Hearts
              Community
              </p>
          </div>"""

            # Create message
            msg = Message(
                subject="Reset Your Password",
                sender=os.getenv("MAIL_USERNAME"),
                recipients=[email],
                html=html_body,
            )

            mail.send(msg)

            return make_response(
                jsonify({"message": "Password reset link sent to your email"}), 200
            )
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            db.session.rollback()
            return make_response(
                jsonify(
                    {
                        "error": "An error occurred while sending the email. Please try again later."
                    }
                ),
                500,
            )


class ResetPassword(Resource):
    def post(self):
        data = request.json
        token = data.get("token")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        account_type = data.get("account_type")

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
        entity.password_hash = generate_password_hash(new_password)

        # Delete the reset token after use
        db.session.delete(reset_token_entry)
        db.session.commit()

        return make_response(
            jsonify({"msg": "Password has been reset successfully"}), 200
        )


class EmailChange(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get("userId")
        account_type = data.get("accountType")

        if not email:
            return make_response(jsonify({"error": "Email is required"}), 400)

        if account_type == "user":
            user = User.query.filter_by(user_id=user_id).first()
            if user:
                entity_id = user.user_id
                entity_email = user.email

            else:
                return make_response(
                    jsonify({"error": "No user found with that email"}), 404
                )

        elif account_type == "parent":
            parent = Parent.query.filter_by(parent_id=user_id).first()
            if parent:
                entity_id = parent.parent_id
                entity_email = parent.email
                entity_type = "parent"
            else:
                return make_response(
                    jsonify({"error": "No parent found with that user_id"}), 404
                )

        elif account_type == "provider":
            provider = Provider.query.filter_by(provider_id=user_id).first()
            if provider:
                entity_id = provider.provider_id
                entity_type = "provider"
                entity_email = provider.email
            else:
                return make_response(
                    jsonify({"error": "No provider found with that email"}), 404
                )

        else:
            return make_response(jsonify({"msg": "Invalid account type"}), 400)

        # Generate a unique 5-digit reset token
        reset_token = self.get_unique_reset_token()

        # Create a ResetToken entry with a 1-hour expiry
        reset_token_entry = ResetToken(
            token=reset_token, expires_at=datetime.utcnow() + timedelta(hours=1)
        )

        # Associate reset token with the entity
        if entity_type == "user":
            reset_token_entry.user_id = entity_id
        elif entity_type == "parent":
            reset_token_entry.parent_id = entity_id
        elif entity_type == "provider":
            reset_token_entry.provider_id = entity_id

        # Save token to the database
        db.session.add(reset_token_entry)
        db.session.commit()

        try:

            expiration_time = "1 hour"

            html_body = f"""
                    <div
                    style="width: 100%;background: #ebf2fa;padding: 20px 0 0 0;font-family: system-ui, sans-serif; text-align: center;">
                    <div
                    style="border-top: 6px solid #007BFF; background-color: #fff; display: block; padding:  8px 20px; text-align: center;   max-width: 500px;  border-bottom-left-radius: .4rem; border-bottom-right-radius: .4rem; letter-spacing: .037rem; line-height: 26px;  margin: auto; font-size: 14px; ">
                    <!-- Logo -->
                    <img src="https://res.cloudinary.com/droynil1n/image/upload/v1728204000/e50iplialg1fawi16enn.png"
                        alt="Happy Hearts Logo" style="width: 70%; height: auto; margin:auto">
                    <!-- Content Section -->
                    <div style="text-align: left; padding-top: 10px;">
                        <p style="text-align: center;">You have requested to change your email address, to confirm change please enter the provided code
                        </p>
                    </div>
                        <h1>{reset_token}</h1>

                    <!-- Additional Information -->
                    <div style="text-align: center; padding-top: 2px;">
                        <p>Code  expires in <strong>{expiration_time}</strong>.</p>
                        <p> For assistance, reach us at
                        <a href='mailto:{os.getenv(' MAIL_USERNAME')}'
                            style='color: #007BFF; text-decoration: underline;'>{os.getenv('MAIL_USERNAME')}</a>.
                        </p>
                    </div>
                    </div>
                    <p style="padding: 20px 0 5px 0; text-align: center;color: rgb(150, 150, 150);font-size: 12px;">Happy Hearts
                    Community
                    </p>
                    </div>"""

            # Create message
            msg = Message(
                subject="Email Verification",
                sender=os.getenv("MAIL_USERNAME"),
                recipients=[entity_email],
                html=html_body,
            )

            mail.send(msg)

            return make_response(
                jsonify({"msg": " verification code sent to your old email"}), 201
            )
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            db.session.rollback()
            return make_response(
                jsonify(
                    {
                        "error": "An error occurred while sending the email. Please try again later."
                    }
                ),
                500,
            )

    def get_unique_reset_token(self):
        """Generates a unique 5-digit reset token."""
        while True:
            reset_token = str(random.randint(10000, 99999))
            token_exists = ResetToken.query.filter_by(token=reset_token).first()
            if not token_exists:
                return reset_token

    def patch(self, email, token):
        if not token:
            return make_response(jsonify({"msg": "Token is required"}), 400)

        reset_token_entry = ResetToken.query.filter_by(token=token).first()

        if not reset_token_entry:
            return make_response(jsonify({"msg": "Invalid or expired token"}), 400)

        # Check if the token is expired
        if reset_token_entry.expires_at < datetime.utcnow():
            db.session.delete(reset_token_entry)
            db.session.commit()
            return make_response(jsonify({"msg": "Token has expired"}), 400)

        try:
            entity = None
            if reset_token_entry.user_id:
                entity = User.query.filter_by(user_id=reset_token_entry.user_id).first()
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    return make_response(
                        jsonify({"msg": "This email address is already in use."}), 409
                    )

            elif reset_token_entry.parent_id:
                entity = Parent.query.filter_by(
                    parent_id=reset_token_entry.parent_id
                ).first()
                existing_parent = Parent.query.filter_by(email=email).first()
                if existing_parent:
                    return make_response(
                        jsonify({"msg": "This email address is already in use."}), 409
                    )

            elif reset_token_entry.provider_id:
                entity = Provider.query.filter_by(
                    provider_id=reset_token_entry.provider_id
                ).first()
                existing_provider = Provider.query.filter_by(email=email).first()
                if existing_provider:
                    return make_response(
                        jsonify({"msg": "This email address is already in use."}), 409
                    )

            if entity:
                entity.email = email
                db.session.delete(reset_token_entry)
                db.session.commit()
            try:

                html_body = f"""
                        <div
                        style="width: 100%;background: #ebf2fa;padding: 20px 0 0 0;font-family: system-ui, sans-serif; text-align: center;">
                        <div
                        style="border-top: 6px solid #007BFF; background-color: #fff; display: block; padding:  8px 20px; text-align: center;   max-width: 500px;  border-bottom-left-radius: .4rem; border-bottom-right-radius: .4rem; letter-spacing: .037rem; line-height: 26px;  margin: auto; font-size: 14px; ">
                        <!-- Logo -->
                        <img src="https://res.cloudinary.com/droynil1n/image/upload/v1728204000/e50iplialg1fawi16enn.png"
                            alt="Happy Hearts Logo" style="width: 70%; height: auto; margin:auto">
                        <!-- Content Section -->
                        <div style="text-align: left; padding-top: 10px;">
                            <p style="text-align: center;">Email has been updated sucessfully. This will be the new channel of infomation future updates and logins</p>
                        </div>

                        <!-- Additional Information -->
                        <div style="text-align: center; padding-top: 2px;">
                            <p> For assistance, reach us at
                            <a href='mailto:{os.getenv(' MAIL_USERNAME')}'
                                style='color: #007BFF; text-decoration: underline;'>{os.getenv('MAIL_USERNAME')}</a>.
                            </p>
                        </div>
                        </div>
                        <p style="padding: 20px 0 5px 0; text-align: center;color: rgb(150, 150, 150);font-size: 12px;">Happy Hearts
                        Community
                        </p>
                        </div>"""

                # Create message
                msg = Message(
                    subject="Email Update",
                    sender=os.getenv("MAIL_USERNAME"),
                    recipients=[email],
                    html=html_body,
                )

                mail.send(msg)

                return make_response(jsonify({"msg": " Email Update sucessful"}), 200)
            except Exception as e:
                logger.error(f"Error sending password reset email: {e}")
                db.session.rollback()
                return make_response(
                    jsonify({"msg": f"{e}, Check your mail and try Again"}),
                    500,
                )

            return make_response(
                jsonify({"msg": "Email has been changed successfully"}), 200
            )
        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(e.orig):
                return make_response(
                    jsonify({"msg": "This email address is already in use."}), 400
                )
            return make_response(
                jsonify({"msg": "Database integrity error occurred"}), 400
            )
        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)
