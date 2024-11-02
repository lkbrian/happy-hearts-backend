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
            return make_json_response("No input data provided", 400)
        parent = None
        child = None

        provider_id = data.get("provider_id")
        provider = Provider.query.filter_by(provider_id=provider_id).first()

        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)

        national_id = data.get("national_id")
        parent_id = data.get("parent_id")
        child_id = data.get("child_id")
        certificate_No = data.get("certificate_No")

        if (child_id or certificate_No) and (parent_id or national_id):
            return make_response(
                jsonify({"msg": "Prescription belongs to either parent or child"}), 400
            )
        if national_id or parent_id:
            parent = (
                Parent.query.filter_by(national_id=national_id).first()
                or Parent.query.filter_by(parent_id=parent_id).first()
            )
            if not parent:
                return make_response(jsonify({"msg": "Parent not found"}), 404)
        if child_id or certificate_No:
            child = Child.query.filter_by(certificate_No=certificate_No).first()
            if not child:
                return make_response(jsonify({"msg": "Child not found"}), 404)

        # Ensure required fields are present
        medicine_id = data.get("medicine_id")
        provider_id = data.get("provider_id")
        quantity = data.get("quantity")
        dosage = data.get("dosage")
        filled_date_str = data.get("filled_date")
        expiry_date_str = data.get("expiry_date")

        if (
            not medicine_id
            or not quantity
            or not dosage
            or not filled_date_str
            or not expiry_date_str
        ):
            return make_json_response(
                "Medicine ID, quantity, dosage, filled date, and expiry date are required",
                400,
            )

        # Attempt to parse dates
        try:
            filled_date = datetime.strptime(filled_date_str, "%Y-%m-%d")
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
        except ValueError:
            return make_json_response("Invalid date format. Use YYYY-MM-DD", 400)

        provider = Provider.query.get(provider_id)
        medicine = Medicine.query.get(medicine_id)

        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)
        if not medicine:
            return make_response(jsonify({"msg": "Medicine not found"}), 404)
        try:
            prescription = Prescription(
                medicine_id=medicine_id,
                quantity=quantity,
                dosage=dosage,
                duration=data.get("duration"),
                parent_id=parent.parent_id if parent else None,
                child_id=child.child_id if child else None,
                provider_id=provider.provider_id,
                filled_date=filled_date,
                expiry_date=expiry_date,
                refill_count=data.get("refill_count", 0),
            )

            db.session.add(prescription)
            db.session.commit()
            return make_json_response("Prescription created successfully", 201)

        except IntegrityError as e:
            db.session.rollback()
            print(e)
            return make_json_response(f"Integrity constraint failed,{e}", 400)

        except Exception as e:
            db.session.rollback()  # Ensure rollback on unexpected error
            return make_json_response(str(e), 500)

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
                                jsonify({"msg": "Invalid date format. Use YYYY-MM-DD"}),
                                400,
                            )

                    if key in ["parent_id", "national_id"]:
                        parent = (
                            Parent.query.filter_by(
                                parent_id=data.get("parent_id")
                            ).first()
                            or Parent.query.filter_by(
                                national_id=data.get("national_id")
                            ).first()
                        )

                        if not parent:
                            return make_response(
                                jsonify({"msg": "Parent not found"}), 404
                            )
                        else:
                            value = parent.parent_id

                    elif key == "certificate_No":
                        child = Child.query.filter_by(certificate_No=value).first()
                        if not child:
                            return make_response(
                                jsonify({"msg": "Child not found"}), 404
                            )
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


class PrescriptionForParent(Resource):
    def get(self, id):
        prescription = [
            p.to_dict() for p in Prescription.query.filter_by(parent_id=id).all()
        ]
        if prescription:
            response = make_response(jsonify(prescription), 200)
            return response


class PrescriptionForProvider(Resource):
    def get(self, id):
        prescription = [
            p.to_dict() for p in Prescription.query.filter_by(provider_id=id).all()
        ]
        if prescription:
            response = make_response(jsonify(prescription), 200)
            return response


class PrescriptionForChild(Resource):
    def get(self, id):
        prescription = [
            p.to_dict() for p in Prescription.query.filter_by(child_id=id).all()
        ]
        if prescription:
            response = make_response(jsonify(prescription), 200)
            return response


def make_json_response(message, status_code=200):
    return make_response(jsonify({"msg": message}), status_code)


def find_parent_or_child(national_id=None, child_certificate_no=None):
    if national_id:
        parent = Parent.query.get(national_id)
        if parent:
            return parent.parent_id
    elif child_certificate_no:
        child = Child.query.filter_by(certificate_No=child_certificate_no).first()
        if child:
            return child.child_id
    return None
