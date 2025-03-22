from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Child, Discharge_summary, Parent, Provider, Admission
from config import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime


class DischargeSummaryAPI(Resource):
    def get(self, id=None):
        if id is None:
            summaries = [d.to_dict() for d in Discharge_summary.query.all()]
            return make_response(jsonify(summaries), 200)
        else:
            summary = Discharge_summary.query.filter_by(discharge_id=id).first()
            if not summary:
                return make_response(
                    jsonify({"msg": "Discharge summary not found"}), 404
                )
            return make_response(jsonify(summary.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)
        provider_id = data.get("provider_id")
        admission_id = data.get("admission_id")
        provider_id = data.get("provider_id")
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
        provider = Provider.query.filter_by(provider_id=provider_id)
        admission = Admission.query.filter_by(admission_id=admission_id)
        if not provider:
            return make_json_response("Provider not found", 404)

        if not admission:
            return make_response(jsonify({"msg": "Admission not found"}), 404)

        try:
            summary = Discharge_summary(
                admission_id=admission.admission_id,
                admission_date=admission.admission_date,
                discharge_date=datetime.strptime(
                    data["discharge_date"], "%Y-%m-%d %H:%M"
                ),
                discharge_diagnosis=data["discharge_diagnosis"],
                procedure=data.get("procedure"),
                parent_id=validation_result.get("parent", {}).get("parent_id"),
                child_id=validation_result.get("child", {}).get("child_id"),
                provider_id=data["provider_id"],
            )
            db.session.add(summary)
            db.session.commit()

            return make_response(
                jsonify({"msg": "Discharge summary created successfully"}), 201
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self, id):
        data = request.json
        if not data:
            return jsonify({"msg": "No input provided"})

        summary = Discharge_summary.query.filter_by(discharge_id=id).first()
        if not summary:
            return jsonify({"msg": "Discharge summary not found"})

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

                if hasattr(summary, field):
                    setattr(summary, field, value)

            db.session.commit()
            return make_response(
                jsonify({"msg": "Discharge summary updated successfully"}), 200
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        summary = Discharge_summary.query.filter_by(discharge_id=id).first()

        if not summary:
            return jsonify({"msg": "Discharge summary not found"})
        db.session.delete(summary)
        db.session.commit()

        return make_response(
            jsonify({"msg": "Discharge summary deleted successfully"}), 200
        )


class DischargeForParent(Resource):
    def get(self, id):
        discharges = [
            d.to_dict() for d in Discharge_summary.query.filter_by(parent_id=id).all()
        ]
        if discharges:
            response = make_response(jsonify(discharges), 200)
            return response


class DischargeForProvider(Resource):
    def get(self, id):
        discharges = [
            d.to_dict() for d in Discharge_summary.query.filter_by(provider_id=id).all()
        ]
        if discharges:
            response = make_response(jsonify(discharges), 200)
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
