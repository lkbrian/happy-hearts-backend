from config import db, mail
from flask_restful import Resource
from models import Appointment, Provider, Parent
from flask import make_response, jsonify, request
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
from flask_mail import Message
from venv import logger
import pytz

EAT = pytz.timezone("Africa/Nairobi")


class appointmentsAPI(Resource):
    def get(self, id=None):
        if id is None:
            appointments = [a.to_dict() for a in Appointment.query.all()]
            response = make_response(jsonify(appointments), 200)
            return response
        else:
            appointment = Appointment.query.filter_by(appointment_id=id).first()
            response = make_response(jsonify(appointment.to_dict()), 200)
            return response

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        # Parse the appointment date from the input
        try:
            appointment_date = datetime.strptime(
                data["appointment_date"], "%Y-%m-%dT%H:%M"
            )
        except ValueError:
            return make_response(
                jsonify({"msg": "Invalid date format, use YYYY-MM-DDTHH:MM"}), 400
            )

        # Convert to localized time in EAT (Africa/Nairobi)
        appointment_date = EAT.localize(appointment_date)
        now = datetime.now(EAT)

        # Ensure appointment is not scheduled in the past
        if appointment_date < now:
            return make_response(
                jsonify({"msg": "Enter a date later than today or today"}), 400
            )

        # Retrieve national ID, parent, and provider from input
        national_id = data.get("national_id")
        parent_id = data.get("parent_id")
        provider_id = data.get("provider_id")

        parent = (
            Parent.query.filter_by(national_id=national_id).first()
            or Parent.query.filter_by(parent_id=parent_id).first()
        )
        provider = Provider.query.filter_by(provider_id=provider_id).first()

        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)
        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)

        try:
            # Create the new appointment
            appointment = Appointment(
                parent_id=parent.parent_id,
                provider_id=provider.provider_id,
                reason=data["reason"],
                appointment_date=appointment_date,
                status=data.get("status"),
            )
            db.session.add(appointment)
            db.session.commit()

            # Send email after appointment creation
            try:
                appointment_date_str = appointment_date.strftime(
                    "%Y-%m-%d %H:%M"
                )  # Convert datetime to string

                html_body = f"""
                <div style="width: 100%;background: #ebf2fa;padding: 20px 0 0 0;font-family: system-ui, sans-serif; text-align: center;">
                    <div style="border-top: 6px solid #007BFF; background-color: #fff; display: block; padding: 8px 20px; text-align: center; max-width: 500px; border-bottom-left-radius: .4rem; border-bottom-right-radius: .4rem; letter-spacing: .037rem; line-height: 26px; margin: auto; font-size: 14px;">
                        <img src="https://res.cloudinary.com/droynil1n/image/upload/v1728204000/e50iplialg1fawi16enn.png"
                            alt="Happy Hearts Logo" style="width: 70%; height: auto; margin:auto">
                        <div style="text-align: left; padding-top: 10px;">
                            <p>An appointment for you has been scheduled by {provider.name} set for {appointment_date_str}.</p>
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
                    subject="Appointment schedule",
                    sender=os.getenv("MAIL_USERNAME"),
                    recipients=[recipient_email],
                    html=html_body,
                )

                mail.send(msg)

                return make_response(
                    jsonify({"msg": "Appointment created and email sent successfully"}),
                    201,
                )
            except Exception as e:
                logger.error(f"Error sending appointment email: {e}")
                db.session.rollback()
                return make_response(
                    jsonify(
                        {
                            "error": "An error occurred while sending the email. Please try again later."
                        }
                    ),
                    500,
                )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return jsonify({"msg": str(e)}), 500

    def patch(self, id):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        appointment = Appointment.query.filter_by(id=id).first()
        if not appointment:
            return make_response(jsonify({"msg": "Appointment doesn't exist"}), 404)

        try:
            for field, value in data.items():
                if field == "appointment_date":  # Handle date conversion
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d %H:%M")
                    except ValueError:
                        return make_response(
                            jsonify(
                                {
                                    "msg": f"Invalid date format for {field}, should be YYYY-MM-DD"
                                }
                            ),
                            400,
                        )

                elif field == "parent_id":
                    parent = Parent.query.get(data.get("parent_id"))
                    if not parent:
                        return make_response(jsonify({"msg": "Parent not found"}), 404)

                elif field == "provider_id":
                    provider = Provider.query.get(data.get("provider_id"))
                    if not provider:
                        return make_response(
                            jsonify({"msg": "Provider not found"}), 404
                        )
                if hasattr(appointment, field):
                    setattr(appointment, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Appointment updated succesfully"}), 201
            )
        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def delete(self, id):
        appointment = Appointment.query.filter_by(appointment_id=id).first()
        if not appointment:
            return make_response(jsonify({"msg": "Appointment doesn't exist"}), 404)
        db.session.delete(appointment)
        return make_response(jsonify({"msg": "Appointment deleted sucesfully"}), 200)


class AppointmentForParent(Resource):
    def get(self, id):
        appointments = [
            a.to_dict() for a in Appointment.query.filter_by(parent_id=id).all()
        ]
        if appointments:
            response = make_response(jsonify(appointments), 200)
            return response


class AppointmentForProvider(Resource):
    def get(self, id):
        appointments = [
            a.to_dict() for a in Appointment.query.filter_by(provider_id=id).all()
        ]
        if appointments:
            response = make_response(jsonify(appointments), 200)
            return response


class ApproveAppointment(Resource):
    def patch(self, id):
        data = request.json
        if not data or "status" not in data:
            return make_response(jsonify({"msg": "No status provided"}), 400)

        # Fetch the appointment
        appointment = Appointment.query.filter_by(appointment_id=id).first()
        if not appointment:
            return make_response(jsonify({"msg": "Appointment not found"}), 404)

        # Check if the current status is "Waiting Approval"
        if appointment.status != "Waiting Approval":
            return make_response(
                jsonify({"msg": "Appointment is not awaiting approval"}), 400
            )

        try:
            # Update the status based on the input
            new_status = data.get("status")
            rejection_reason = data.get("rejection_reason", None)

            if new_status == "Approved":
                appointment.status = "Approved"
                db.session.commit()

                # Send approval email
                self.send_approval_email(appointment)

                return make_response(jsonify({"msg": "Appointment approved"}), 200)

            elif new_status == "Rejected":
                if not rejection_reason:
                    return make_response(
                        jsonify({"msg": "Rejection reason is required"}), 400
                    )

                appointment.status = "Rejected"
                appointment.rejection_reason = rejection_reason  # Save the reason
                db.session.commit()

                # Send rejection email
                self.send_rejection_email(appointment, rejection_reason)

                return make_response(jsonify({"msg": "Appointment rejected"}), 200)

            else:
                return make_response(jsonify({"msg": "Invalid status"}), 400)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def send_approval_email(self, appointment):
        try:
            # Prepare email content
            provider = appointment.provider
            appointment_date_str = appointment.appointment_date.strftime(
                "%Y-%m-%d %H:%M"
            )
            html_body = f"""
            <div style="width: 100%;background: #ebf2fa;padding: 20px 0 0 0;font-family: system-ui, sans-serif; text-align: center;">
                <div style="border-top: 6px solid #007BFF; background-color: #fff; display: block; padding: 8px 20px; text-align: center; max-width: 500px; border-bottom-left-radius: .4rem; border-bottom-right-radius: .4rem; letter-spacing: .037rem; line-height: 26px; margin: auto; font-size: 14px;">
                    <img src="https://res.cloudinary.com/droynil1n/image/upload/v1728204000/e50iplialg1fawi16enn.png"
                        alt="Happy Hearts Logo" style="width: 70%; height: auto; margin:auto">
                    <div style="text-align: left; padding-top: 10px;">
                        <p>Your appointment with {provider.name} on {appointment_date_str} has been <strong>approved</strong>.</p>
                    </div>
                    <div style="text-align: center; padding-top: 2px;">
                        <p>If you have any questions, contact us at
                        <a href='mailto:{os.getenv('MAIL_USERNAME')}'
                            style='color: #007BFF; text-decoration: underline;'>{os.getenv('MAIL_USERNAME')}</a>.
                        </p>
                    </div>
                </div>
                <p style="padding: 20px 0 5px 0; text-align: center;color: rgb(150, 150, 150);font-size: 12px;">Happy Hearts Community
                </p>
            </div>"""

            recipient_email = appointment.parent.email.strip()

            # Send email message
            msg = Message(
                subject="Appointment Approved",
                sender=os.getenv("MAIL_USERNAME"),
                recipients=[recipient_email],
                html=html_body,
            )

            mail.send(msg)
            logger.info(f"Approval email sent to {recipient_email}")
        except Exception as e:
            logger.error(f"Error sending approval email: {e}")

    def send_rejection_email(self, appointment, rejection_reason):
        try:
            # Prepare email content
            provider = appointment.provider
            html_body = f"""
            <div style="width: 100%;background: #ebf2fa;padding: 20px 0 0 0;font-family: system-ui, sans-serif; text-align: center;">
                <div style="border-top: 6px solid #007BFF; background-color: #fff; display: block; padding: 8px 20px; text-align: center; max-width: 500px; border-bottom-left-radius: .4rem; border-bottom-right-radius: .4rem; letter-spacing: .037rem; line-height: 26px; margin: auto; font-size: 14px;">
                    <img src="https://res.cloudinary.com/droynil1n/image/upload/v1728204000/e50iplialg1fawi16enn.png"
                        alt="Happy Hearts Logo" style="width: 70%; height: auto; margin:auto">
                    <div style="text-align: left; padding-top: 10px;">
                        <p>Your appointment with {provider.name} was <strong>rejected</strong>.</p>
                        <p>Reason: {rejection_reason}</p>
                    </div>
                    <div style="text-align: center; padding-top: 2px;">
                        <p>If you have any questions, contact us at
                        <a href='mailto:{os.getenv('MAIL_USERNAME')}'
                            style='color: #007BFF; text-decoration: underline;'>{os.getenv('MAIL_USERNAME')}</a>.
                        </p>
                    </div>
                </div>
                <p style="padding: 20px 0 5px 0; text-align: center;color: rgb(150, 150, 150);font-size: 12px;">Happy Hearts Community
                </p>
            </div>"""

            recipient_email = appointment.parent.email.strip()

            # Send email message
            msg = Message(
                subject="Appointment Rejected",
                sender=os.getenv("MAIL_USERNAME"),
                recipients=[recipient_email],
                html=html_body,
            )

            mail.send(msg)
            logger.info(f"Rejection email sent to {recipient_email}")
        except Exception as e:
            logger.error(f"Error sending rejection email: {e}")
