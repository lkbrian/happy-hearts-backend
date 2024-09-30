from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Discharge_summary,Parent,Provider
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

        national_id = data.get("national_id")
        parent_id = data.get("parent_id")

        parent = Parent.query.filter_by(national_id=national_id).first() or Parent.query.filter_by(parent_id=parent_id).first()

        provider = Provider.query.get(data.get("provider_id"))

        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)

        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)
        try:
            summary = Discharge_summary(
                admission_date=datetime.strptime(data["admission_date"], "%Y-%m-%d %H:%M"),
                discharge_date=datetime.strptime(data["discharge_date"], "%Y-%m-%d %H:%M"),
                discharge_diagnosis=data["discharge_diagnosis"],
                procedure=data.get("procedure"),
                parent_id=parent.parent_id,
                provider_id=data["provider_id"],
            )
            db.session.add(summary)
            db.session.commit()

            return make_response(
                jsonify({"msg": "Discharge summary created successfully"}), 201
            )

        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({"msg": "Integrity constraint failed"}), 400)

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
                        return make_response(jsonify({"msg": "Provider not found"}), 404)                
                if hasattr(summary, field):
                    setattr(summary, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Discharge summary updated successfully"}), 200
            )

        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({"msg": "Integrity constraint failed"}), 400)

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
