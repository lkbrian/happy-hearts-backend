from flask_restful import Resource
from flask import request, jsonify, make_response
from models import Child, Medications, Parent, Provider
from config import db
from sqlalchemy.exc import IntegrityError


class MedicationsAPI(Resource):
    def get(self, id=None):
        if id is None:
            medications = [med.to_dict() for med in Medications.query.all()]
            return make_response(jsonify(medications), 200)
        else:
            medication = Medications.query.filter_by(medication_id=id).first()
            if not medication:
                return jsonify({"msg": "Medication not found"}), 404
            return make_response(jsonify(medication.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_json_response("No input data provided", 400)

        # Validate responsible party (parent or child) using find_parent_or_child
        validation_result = find_parent_or_child(
            parent_id=data.get("parent_id"),
            child_certificate_no=data.get("child_certificate_no"),
        )

        # Ensure valid relationship (either parent or child)
        if validation_result is None:
            return make_json_response(
                "Medication must belong to either a parent or child, not both", 400
            )

        # Verify Provider exists
        provider = Provider.query.get(data.get("provider_id"))
        if not provider:
            return make_json_response("Provider not found", 404)

        # Create medication record
        try:
            medication = Medications(
                name=data.get("name"),
                size_in_mg=data.get("size_in_mg"),
                dose_in_mg=data.get("dose_in_mg"),
                route=data.get("route"),
                dose_per_day=data.get("dose_per_day"),
                referral=data.get("referral"),
                provider_id=data["provider_id"],
                parent_id=validation_result.get("parent", {}).get("parent_id"),
                child_id=validation_result.get("child", {}).get("child_id"),
            )
            db.session.add(medication)
            db.session.commit()
            return make_json_response("Medication created successfully", 201)

        except IntegrityError:
            db.session.rollback()
            return make_json_response("Integrity constraint failed", 400)

        except Exception as e:
            return make_json_response(str(e), 500)

    def patch(self, id):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        medication = Medications.query.filter_by(medication_id=id).first()
        if not medication:
            return make_response(jsonify({"msg": "Medication not found"}), 404)

        try:
            for field, value in data.items():
                if field == "parent_id":
                    parent = Parent.query.get(value)
                    if not parent:
                        return make_response(jsonify({"msg": "Parent not found"}), 404)

                elif field == "provider_id":
                    provider = Provider.query.get(value)
                    if not provider:
                        return make_response(
                            jsonify({"msg": "Provider not found"}), 404
                        )

                if hasattr(medication, field):
                    setattr(medication, field, value)

            db.session.commit()
            return make_response(
                jsonify({"msg": "Medication updated successfully"}), 200
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        medication = Medications.query.filter_by(medication_id=id).first()
        if not medication:
            return jsonify({"msg": "Medication not found"})
        db.session.delete(medication)
        db.session.commit()
        return make_response(jsonify({"msg": "Medication deleted successfully"}), 200)


class MedicationForParents(Resource):
    def get(self, id):
        meds = [a.to_dict() for a in Medications.query.filter_by(parent_id=id).all()]
        if meds:
            response = make_response(jsonify(meds), 200)
            return response


class MedicationForProviders(Resource):
    def get(self, id):
        meds = [a.to_dict() for a in Medications.query.filter_by(provider_id=id).all()]
        if meds:
            response = make_response(jsonify(meds), 200)
            return response


class MedicationForChild(Resource):
    def get(self, id):
        meds = [a.to_dict() for a in Medications.query.filter_by(child_id=id).all()]
        if meds:
            response = make_response(jsonify(meds), 200)
            return response


def find_parent_or_child(parent_id=None, child_certificate_no=None):
    if parent_id:
        parent = Parent.query.get(parent_id)
        if parent:
            return {"parent": parent}
    elif child_certificate_no:
        child = Child.query.filter_by(certificate_No=child_certificate_no).first()
        if child:
            return {"child": child}
    return None


def make_json_response(message, status_code=200):
    return make_response(jsonify({"msg": message}), status_code)
