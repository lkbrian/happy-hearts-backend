from flask_restful import Resource
from flask import request, jsonify, make_response
from models import Present_pregnancy,Parent
from config import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime


class PresentPregnancyAPI(Resource):
    def get(self, id=None):
        if id is None:
            pregnancies = [preg.to_dict() for preg in Present_pregnancy.query.all()]
            return make_response(jsonify(pregnancies), 200)
        else:
            pregnancy = Present_pregnancy.query.filter_by(pp_id=id).first()
            if not pregnancy:
                return jsonify({"msg": "Present pregnancy not found"}), 404
            return make_response(jsonify(pregnancy.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)
        parent_id=data["parent_id"]

        parent=Parent.query.filter_by(parent_id=parent_id)
        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)
        try:
            pregnancy = Present_pregnancy(
                date=datetime.strptime(data["date"], "%Y-%m-%d %H:%M"),
                weight_in_kg=data["weight_in_kg"],
                urinalysis=data["urinalysis"],
                blood_pressure=data["blood_pressure"],
                pollar=data["pollar"],
                maturity_in_weeks=data["maturity_in_weeks"],
                fundal_height=data["fundal_height"],
                comments=data["comments"],
                clinical_notes=data["clinical_notes"],
                parent_id=parent.parent_id
            )
            db.session.add(pregnancy)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Present pregnancy created successfully"}), 201
            )

        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def patch(self, id):
        data = request.json
        if not data:
            return jsonify({"msg": "No input provided"}), 400

        pregnancy = Present_pregnancy.query.filter_by(pp_id=id).first()
        if not pregnancy:
            return jsonify({"msg": "Present pregnancy not found"}), 404

        try:
            for field, value in data.items():
                
                if hasattr(pregnancy, field):
                    setattr(pregnancy, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Present pregnancy updated successfully"}), 200
            )

        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def delete(self, id):
        pregnancy = Present_pregnancy.query.filter_by(pp_id=id).first()
        if not pregnancy:
            return jsonify({"msg": "Present pregnancy not found"}), 404
        db.session.delete(pregnancy)
        db.session.commit()
        return make_response(
            jsonify({"msg": "Present pregnancy deleted successfully"}), 200
        )
