# custom_types.py
import json
from sqlalchemy.types import TypeDecorator, VARCHAR
from datetime import datetime
import pytz
from config import db, app, mail
from models import Appointment, Birth
import logging
import os
from flask import make_response, jsonify
from flask_mail import Message
from venv import logger
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt


logging.basicConfig(level=logging.INFO)


def update_appointment_statuses():
    with app.app_context():
        now = datetime.now(pytz.timezone("Africa/Nairobi"))  # Current time in EAT
        logging.info(f"Running update at {now}")

        # Query appointments where the appointment date is in the past and status is pending
        appointments = Appointment.query.filter(
            Appointment.appointment_date <= now, Appointment.status == "pending"
        ).all()

        if not appointments:
            logging.info("No appointments to update.")
            return make_response(jsonify({"msg": "No appointments to update."}), 200)

        for appointment in appointments:
            try:
                # Update the appointment status to 'missed'
                appointment.status = "missed"
                db.session.add(
                    appointment
                )  # Add the appointment to the session after updating the status

                # Prepare the email body
                appointment_date_str = appointment.appointment_date.strftime(
                    "%Y-%m-%d %H:%M"
                )

                html_body = f"""
                <div style="width: 100%;background: #ebf2fa;padding: 20px 0 0 0;font-family: system-ui, sans-serif; text-align: center;">
                    <div style="border-top: 6px solid #007BFF; background-color: #fff; display: block; padding: 8px 20px; text-align: center; max-width: 500px; border-bottom-left-radius: .4rem; border-bottom-right-radius: .4rem; letter-spacing: .037rem; line-height: 26px; margin: auto; font-size: 14px;">
                        <img src="https://res.cloudinary.com/droynil1n/image/upload/v1728204000/e50iplialg1fawi16enn.png"
                            alt="Happy Hearts Logo" style="width: 70%; height: auto; margin:auto">
                        <div style="text-align: left; padding-top: 10px;">
                            <p> You have missed an appointment that was scheduled for {appointment_date_str}.Reason for Appointment: {appointment.reason}.</p>
                        </div>
                        <div style="text-align: center; padding-top: 2px;">
                            <p>For assistance, reach us at
                            <a href='mailto:{os.getenv('MAIL_USERNAME')}'
                                style='color: #007BFF; text-decoration: underline;'>{os.getenv('MAIL_USERNAME')}</a>.
                            </p>
                        </div>
                    </div>
                    <p style="padding: 20px 0 5px 0; text-align: center;color: rgb(150, 150, 150);font-size: 12px;">Happy Hearts
                    Community
                    </p>
                </div>"""

                recipient_email = appointment.parent.email.strip()

                # Send email message
                msg = Message(
                    subject="Missed Appointment",
                    sender=os.getenv("MAIL_USERNAME"),
                    recipients=[recipient_email],
                    html=html_body,
                )
                mail.send(msg)

                logging.info(
                    f"Email sent to {recipient_email} for appointment {appointment.appointment_id}"
                )

            except Exception as e:
                logger.error(f"Error sending appointment email: {e}")
                db.session.rollback()  # Rollback transaction in case of error
                continue  # Skip to the next appointment in case of error

        # Commit all updates after processing all appointments
        try:
            db.session.commit()
            logging.info(f"Appointment statuses updated at {now}")
            return make_response(
                jsonify({"msg": "Appointments updated and emails sent successfully"}),
                200,
            )
        except Exception as e:
            db.session.rollback()  # Rollback in case commit fails
            logger.error(f"Error committing appointment updates: {e}")
            return make_response(
                jsonify({"error": "An error occurred while updating the appointments"}),
                500,
            )


def role_required(required_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["role"] not in required_roles:
                required_roles_str = ", ".join(required_roles)
                return make_response(
                    jsonify(
                        {"msg": f"Access forbidden: Requires {required_roles_str}"}
                    ),
                    403,
                )
            return fn(*args, **kwargs)

        return decorator

    return wrapper


class JSONEncodedList(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return json.loads(value)

    # appointment_date = db.Column(db.DateTime(timezone=True), nullable=False)


def generate_serial_number():
    latest_record = db.session.query(Birth).order_by(Birth.serial_number.desc()).first()
    if latest_record is None:
        return 4953636
    else:
        return latest_record.serial_number + 1
