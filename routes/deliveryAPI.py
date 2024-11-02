from flask import jsonify, make_response, request
from flask_restful import Resource
from models import (
    Delivery,
    Parent,
    Provider,
    Present_pregnancy,
    Previous_pregnancy,
    Birth,
)
from config import db, mail
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from flask_mail import Message
import os
from utils.customs import generate_serial_number


class DeliveryAPI(Resource):
    def get(self, id=None):
        if id is None:
            deliveries = [d.to_dict() for d in Delivery.query.all()]
            return make_response(jsonify(deliveries), 200)
        else:
            delivery = Delivery.query.filter_by(delivery_id=id).first()
            if not delivery:
                return make_response(jsonify({"msg": "Delivery not found"}), 404)
            return make_response(jsonify(delivery.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        # national_id = data.get("national_id")
        # parent_id = data.get("parent_id")
        provider_id = data.get("provider_id")
        present_pregnancy_id = data.get("pregnancy_id")

        provider = Provider.query.filter_by(provider_id=provider_id).first()
        present_pregnancy = Present_pregnancy.query.filter_by(
            pp_id=present_pregnancy_id
        ).first()

        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)
        if not present_pregnancy:
            return make_response(jsonify({"msg": "Pregnacy not found"}), 404)
        parent = (
            Parent.query.filter_by(
                national_id=present_pregnancy.parent.national_id
            ).first()
            # or Parent.query.filter_by(parent_id=parent_id).first()
        )
        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)
        type_of_birth_map = {
            "Single": 1,
            "Twins": 2,
            "Triplets": 3,
            "Quadruplets": 4,
            "Quintuplets": 5,
            "Sextuplets": 6,
            "Septuplets": 7,
            "Octuplets": 8,
            "Nonuplets": 9,
        }

        # Get the type of birth as a number
        type_of_birth_str = data.get("typeOfBirth")
        type_of_birth_num = type_of_birth_map.get(type_of_birth_str)
        try:
            delivery = Delivery(
                present_pregnancy_id=present_pregnancy.pp_id,
                mode_of_delivery=data["mode_of_delivery"],
                date=datetime.strptime(data.get("date"), "%Y-%m-%dT%H:%M"),
                duration_of_labour=data["duration_of_labour"],
                condition_of_mother=data["condition_of_mother"],
                condition_of_baby=data["condition_of_baby"],
                weight_at_birth=data["weight_at_birth"],
                gender=data["gender"],
                fate=data["fate"],
                remarks=data.get("remarks"),
                parent_id=parent.parent_id,
                provider_id=provider.provider_id,
                type_of_birth=data.get("typeOfBirth"),
            )
            db.session.add(delivery)
            present_pregnancy.is_delivered = True
            db.session.commit()

            pregnancy = Previous_pregnancy(
                year=delivery.date.year,
                maturity=present_pregnancy.maturity_in_weeks,
                duration_of_labour=delivery.duration_of_labour,
                type_of_delivery=delivery.mode_of_delivery,
                weight_in_kg=delivery.weight_at_birth,
                gender=delivery.gender,
                fate=delivery.fate,
                puerperium="Normal",
                parent_id=parent.parent_id,
                provider_id=provider.provider_id,
                delivery_id=delivery.delivery_id,
            )
            db.session.add(pregnancy)
            db.session.commit()

            if delivery.fate == "Alive":
                for i in range(type_of_birth_num):
                    birth_record = Birth(
                        delivery_id=delivery.delivery_id,
                        baby_name=data.get("baby_name") or f"Baby {i + 1}",
                        date_of_birth=delivery.date,
                        place_of_birth="Happy Hearts",
                        sub_county="Nairobi",
                        serial_number=generate_serial_number(),
                        weight=delivery.weight_at_birth,
                        gender=delivery.gender,
                        fate=delivery.fate,
                        mother_full_name=delivery.parent.name,
                        mother_national_id=delivery.parent.national_id,
                        provider_id=delivery.provider_id,
                        parent_id=delivery.parent_id,
                        type_of_birth=delivery.type_of_birth,
                    )
                    db.session.add(birth_record)
                db.session.commit()

                msg = Message(
                    subject="Congratulations on Your New Baby!",
                    sender=os.getenv("MAIL_USERNAME"),
                    recipients=[delivery.parent.email],
                    html=f"""
                <div style="width: 100%;background: #ebf2fa;padding: 20px 0 0 0;font-family: system-ui, sans-serif; text-align: center;">
                    <div style="border-top: 6px solid #007BFF; background-color: #fff; display: block; padding: 8px 20px; text-align: center; max-width: 500px; border-bottom-left-radius: .4rem; border-bottom-right-radius: .4rem; letter-spacing: .037rem; line-height: 26px; margin: auto; font-size: 14px;">
                        <img src="https://res.cloudinary.com/droynil1n/image/upload/v1728204000/e50iplialg1fawi16enn.png"
                            alt="Happy Hearts Logo" style="width: 70%; height: auto; margin:auto">
                        <div style="text-align: left; padding-top: 10px;">
                            <p>Congratulations on the birth of your precious baby! 
                        We are overjoyed to share in this special moment with you. 
                        May this new chapter bring you immense joy and cherished memories. 
                        Please remember to update your details under the Births tab at your earliest convenience as its important for your Child's Birth Certificate. 
                        We are here to support you and your growing family!</p>
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
                </div>""",
                )
            else:
                # Condolence email message
                msg = Message(
                    subject="Our Heartfelt Condolences",
                    sender=os.getenv("MAIL_USERNAME"),
                    recipients=[delivery.parent.email],
                    html=f"""
                <div style="width: 100%;background: #ebf2fa;padding: 20px 0 0 0;font-family: system-ui, sans-serif; text-align: center;">
                    <div style="border-top: 6px solid #007BFF; background-color: #fff; display: block; padding: 8px 20px; text-align: center; max-width: 500px; border-bottom-left-radius: .4rem; border-bottom-right-radius: .4rem; letter-spacing: .037rem; line-height: 26px; margin: auto; font-size: 14px;">
                        <img src="https://res.cloudinary.com/droynil1n/image/upload/v1728204000/e50iplialg1fawi16enn.png"
                            alt="Happy Hearts Logo" style="width: 70%; height: auto; margin:auto">
                        <div style="text-align: left; padding-top: 10px;">
                            <p>We are deeply saddened by the loss of your beloved child.
                        "Please accept our heartfelt condolences during this difficult time.
                        Our hearts go out to you, and we are here to offer any support and comfort you may need.
                        Please take all the time you need, and know that you are not alone in your grief.</p>
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
                </div>""",
                )

            # Send the email
            try:
                mail.send(msg)
                return make_response(
                    jsonify(
                        {
                            "msg": "Delivery and related records created successfully, email sent"
                        }
                    ),
                    201,
                )
            except Exception as e:
                print(f"Error sending email: {e}")
                db.session.rollback()
                return make_response(
                    jsonify(
                        {
                            "error": "An error occurred while sending the email. Please try again later."
                        }
                    ),
                    500,
                )
            db.session.commit()

            return make_response(
                jsonify({"msg": "Delivery and related records created successfully"}),
                201,
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f"{error_message}"}), 400)

        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self, id):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        delivery = Delivery.query.filter_by(delivery_id=id).first()
        if not delivery:
            return make_response(jsonify({"msg": "Delivery not found"}), 404)

        try:
            for field, value in data.items():
                if field == "date":
                    try:
                        value = datetime.strptime(value, "%Y-%m-%dT%H:%M")
                    except ValueError:
                        return make_response(
                            jsonify(
                                {
                                    "msg": f"Invalid date format for {field}, should be YYYY-MM-DD HH:MM"
                                }
                            ),
                            400,
                        )

                elif field == "parent_id":
                    parent = Parent.query.get(value)
                    if not parent:
                        return make_response(jsonify({"msg": "Parent not found"}), 404)

                elif field == "provider_id":
                    provider = Provider.query.get(value)
                    if not provider:
                        return make_response(
                            jsonify({"msg": "Provider not found"}), 404
                        )

                if hasattr(delivery, field):
                    setattr(delivery, field, value)

            db.session.commit()
            return make_response(jsonify({"msg": "Delivery updated successfully"}), 200)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        delivery = Delivery.query.filter_by(delivery_id=id).first()

        if not delivery:
            return jsonify({"msg": "Delivery not found"})
        db.session.delete(delivery)
        db.session.commit()

        return make_response(jsonify({"msg": "Delivery deleted successfully"}), 200)


class DeliveryForProvider(Resource):
    def get(self, id):
        deliveries = [
            d.to_dict() for d in Delivery.query.filter_by(provider_id=id).all()
        ]
        if deliveries:
            return make_response(jsonify(deliveries), 200)


class DeliveryForParent(Resource):
    def get(self, id):
        deliveries = [d.to_dict() for d in Delivery.query.filter_by(parent_id=id).all()]
        if deliveries:
            return make_response(jsonify(deliveries), 200)
