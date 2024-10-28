from flask_restful import Resource
from flask import request, jsonify, make_response
from models import Previous_pregnancy, Parent, Provider
from config import db
from sqlalchemy.exc import IntegrityError

# from datetime import datetime


class PreviousPregnancyAPI(Resource):
    def get(self, id=None):
        if id is None:
            pregnancies = [preg.to_dict() for preg in Previous_pregnancy.query.all()]
            return make_response(jsonify(pregnancies), 200)
        else:
            pregnancy = Previous_pregnancy.query.filter_by(pp_id=id).first()
            if not pregnancy:
                return jsonify({"msg": "Previous pregnancy not found"}), 404
            return make_response(jsonify(pregnancy.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        national_id = data.get("national_id")
        parent_id = data.get("parent_id")
        parent = (
            Parent.query.filter_by(national_id=national_id).first()
            or Parent.query.filter_by(parent_id=parent_id).first()
        )
        provider = Provider.query.get(data.get("provider_id"))

        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)
        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)

        try:
            pregnancy = Previous_pregnancy(
                year=data["year"],
                maturity=data["maturity"],
                duration_of_labour=data["duration_of_labour"],
                type_of_delivery=data["type_of_delivery"],
                Weight_in_kg=data["Weight_in_kg"],
                gender=data["gender"],
                fate=data["fate"],
                peurperium=data["peurperium"],
                parent_id=parent.parent_id,
                provider_id=provider.provider_id,
            )
            db.session.add(pregnancy)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Previous pregnancy created successfully"}), 201
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

        pregnancy = Previous_pregnancy.query.filter_by(pp_id=id).first()
        if not pregnancy:
            return jsonify({"msg": "Previous pregnancy not found"}), 404

        try:
            for field, value in data.items():
                if hasattr(pregnancy, field):
                    setattr(pregnancy, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Previous pregnancy updated successfully"}), 200
            )

        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400
        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def delete(self, id):
        pregnancy = Previous_pregnancy.query.filter_by(pp_id=id).first()
        if not pregnancy:
            return jsonify({"msg": "Previous pregnancy not found"}), 404
        db.session.delete(pregnancy)
        db.session.commit()
        return make_response(
            jsonify({"msg": "Previous pregnancy deleted successfully"}), 200
        )
