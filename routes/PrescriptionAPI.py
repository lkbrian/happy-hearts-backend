from flask import jsonify, make_response, request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import db
from models import Medicine, Prescription, Child, Parent, Provider
from datetime import datetime


class PrescriptionAPI(Resource):
    def get(self, id=None):
        if id is None:
            prescriptions = Prescription.query.all()
            prescription_list = [
                prescription.to_dict() for prescription in prescriptions
            ]
            return make_response(jsonify(prescription_list), 200)
        else:
            prescription = Prescription.query.get(id)
            if not prescription:
                return make_response(jsonify({"msg": "Prescription not found"}), 404)
            return make_response(jsonify(prescription.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input data provided"}), 400)

        parent_id = data.get("parent_id")
        provider_id = data.get("provider_id")
        medicine_id = data.get("medicine_id")
        child_id = data.get("child_id")
        national_id = data.get("national_id")
        child_certificate_no = data.get("child_certificate_no")
        filled_date_str = data.get("filled_date")
        provider = Provider.query.get(provider_id)
        medicine = Medicine.query.get(medicine_id)

        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)
        if not medicine:
            return make_response(jsonify({"msg": "Medicine not found"}), 404)
        # Parse the filled_date if provided
        try:
            filled_date = (
                datetime.strptime(filled_date_str.strip(), "%Y-%m-%d")
                if filled_date_str
                else None
            )
        except ValueError:
            return make_response(
                jsonify({"msg": "Invalid date format for filled_date. Use YYYY-MM-DD"}),
                400,
            )

        if (child_certificate_no or child_id) and (parent_id or national_id):
            return make_response(
                jsonify(
                    {"msg": "Prescription belongs to parent or child, can't be both"}
                ),
                400,
            )

        elif child_certificate_no or child_id:

            child = (
                Child.query.filter_by(certificate_No=child_certificate_no).first()
                or Child.query.filter_by(child_id=child_id).first()
            )
            if not child:
                return make_response(jsonify({"msg": "Child not found"}), 404)

            try:
                prescription = Prescription(
                    medicine_id=data.get("medicine_id"),
                    quantity=data.get("quantity"),
                    dosage=data.get("dosage"),
                    duration=data.get("duration"),
                    child_id=child.child_id,
                    parent_id=None,
                    filled_date=filled_date,
                    expiry_date=data.get("expiry_date"),
                    refill_count=data.get("refill_count", 0),
                )
                db.session.add(prescription)
                db.session.commit()
                return make_response(
                    jsonify({"msg": "Prescription for child created successfully"}), 201
                )

            except IntegrityError:
                db.session.rollback()
                return make_response(
                    jsonify({"msg": "Integrity constraint failed"}), 400
                )

            except Exception as e:
                return make_response(jsonify({"msg": str(e)}), 500)

        elif parent_id or national_id:
            parent = (
                Parent.query.filter_by(parent_id=parent_id).first()
                or Parent.query.filter_by(national_id=national_id).first()
            )
            if not parent:
                return make_response(jsonify({"msg": "Parent not found"}), 404)
            try:
                prescription = Prescription(
                    medicine_id=data.get("medicine_id"),
                    quantity=data.get("quantity"),
                    dosage=data.get("dosage"),
                    duration=data.get("duration"),
                    parent_id=parent.parent_id,
                    child_id=None,
                    filled_date=filled_date,
                    expiry_date=data.get("expiry_date"),
                    refill_count=data.get("refill_count", 0),
                )
                db.session.add(prescription)
                db.session.commit()
                return make_response(
                    jsonify({"msg": "Prescription for parent created successfully"}),
                    201,
                )

            except IntegrityError:
                db.session.rollback()
                return make_response(
                    jsonify({"msg": "Integrity constraint failed"}), 400
                )

            except Exception as e:
                return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self, id):
        prescription = Prescription.query.get(id)
        if not prescription:
            return make_response(jsonify({"msg": "Prescription not found"}), 404)

        data = request.json
        try:
            for key, value in data.items():
                if key == "filled_date":
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        return make_response(
                            jsonify({"msg": "Invalid date format. Use YYYY-MM-DD"}), 400
                        )

                if key in ["parent_id", "national_id"]:
                    parent = (
                        Parent.query.filter_by(parent_id=data.get("parent_id")).first()
                        or Parent.query.filter_by(
                            national_id=data.get("national_id")
                        ).first()
                    )

                    if not parent:
                        return make_response(jsonify({"msg": "Parent not found"}), 404)
                    else:
                        value = parent.parent_id

                elif key == "child_certificate_no":
                    child = Child.query.filter_by(certificate_No=value).first()
                    if not child:
                        return make_response(jsonify({"msg": "Child not found"}), 404)
                    else:
                        value = child.child_id

                if hasattr(prescription, key):
                    setattr(prescription, key, value)

            db.session.commit()
            return make_response(
                jsonify({"msg": "Prescription updated successfully"}), 200
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        prescription = Prescription.query.get(id)
        if not prescription:
            return make_response(jsonify({"msg": "Prescription not found"}), 404)

        try:
            db.session.delete(prescription)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Prescription deleted successfully"}), 200
            )

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)
