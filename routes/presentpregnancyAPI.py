from flask_restful import Resource
from flask import request, jsonify, make_response
from models import Present_pregnancy, Parent
from config import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime


class PresentPregnancyAPI(Resource):
    def get(self, id=None):
        if id is None:
            pregnancies = [
                preg.to_dict()
                for preg in Present_pregnancy.query.filter_by(is_delivered=False).all()
            ]
            return make_response(jsonify(pregnancies), 200)
        else:
            pregnancy = Present_pregnancy.query.filter_by(
                pp_id=id, is_delivered=False
            ).first()
            if not pregnancy:
                return jsonify({"msg": "Present pregnancy not found"}), 404
            return make_response(jsonify(pregnancy.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)
        national_id = data["national_id"]
        provider_id = data["provider_id"]

        parent = Parent.query.filter_by(national_id=national_id).first()
        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)
        provider = Parent.query.filter_by(provider_id=provider_id).first()
        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)
        present_pregnancy = Present_pregnancy.query.filter_by(
            parent_id=parent.parent_id, is_delivered=False
        ).first()
        if present_pregnancy:
            return make_response(
                jsonify(
                    {
                        "msg": "Parent already has a registerd a pregnancy you can't register another one until they have delivered"
                    }
                ),
                409,
            )

        try:
            pregnancy = Present_pregnancy(
                date=datetime.strptime(data["date"], "%Y-%m-%d"),
                weight_in_kg=data["weight_in_kg"],
                urinalysis=data["urinalysis"],
                blood_pressure=data["blood_pressure"],
                pollar=data["pollar"],
                maturity_in_weeks=data["maturity_in_weeks"],
                fundal_height=data["fundal_height"],
                comments=data["comments"],
                clinical_notes=data["clinical_notes"],
                parent_id=parent.parent_id,
                provider_id=provider.provider_id,
            )
            db.session.add(pregnancy)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Present pregnancy created successfully"}), 201
            )

        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({"msg": "Integrity constraint failed"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self, id):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        pregnancy = Present_pregnancy.query.filter_by(pp_id=id).first()
        if not pregnancy:
            return make_response(jsonify({"msg": "Present pregnancy not found"}), 404)

        try:
            for field, value in data.items():
                if field == "date":
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        return make_response(
                            jsonify({"msg": "Invalid date format. Use YYYY-MM-DD"}), 400
                        )
                if hasattr(pregnancy, field):
                    setattr(pregnancy, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Present pregnancy updated successfully"}), 200
            )

        except IntegrityError as e:
            db.session.rollback()
            return make_response(
                jsonify({"msg": f"Integrity constraint failed {e}"}), 400
            )

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        pregnancy = Present_pregnancy.query.filter_by(pp_id=id).first()
        if not pregnancy:
            return make_response(jsonify({"msg": "Present pregnancy not found"}), 404)
        db.session.delete(pregnancy)
        db.session.commit()
        return make_response(
            jsonify({"msg": "Present pregnancy deleted successfully"}), 200
        )


class PresentPregnancyForParent(Resource):
    def get(self, id):
        pregnancies = [
            p.to_dict() for p in Present_pregnancy.query.filter_by(parent_id=id).all()
        ]
        if pregnancies:
            response = make_response(jsonify(pregnancies), 200)
            return response


class PresentPregnancyForProvider(Resource):
    def get(self, id):
        pregnancies = [
            p.to_dict() for p in Present_pregnancy.query.filter_by(provider_id=id).all()
        ]
        if pregnancies:
            response = make_response(jsonify(pregnancies), 200)
            return response


class PreviousPregnancyAPI(Resource):
    def get(self, id=None):
        if id is None:
            pregnancies = [
                preg.to_dict()
                for preg in Present_pregnancy.query.filter_by(is_delivered=True).all()
            ]
            return make_response(jsonify(pregnancies), 200)
        else:
            pregnancy = Present_pregnancy.query.filter_by(
                pp_id=id, is_delivered=True
            ).first()
            if not pregnancy:
                return jsonify({"msg": "Present pregnancy not found"}), 404
            return make_response(jsonify(pregnancy.to_dict()), 200)


class PreviousPregnancyForParent(Resource):
    def get(self, id):
        pregnancies = [
            p.to_dict()
            for p in Present_pregnancy.query.filter_by(
                parent_id=id, is_delivered=True
            ).all()
        ]
        if pregnancies:
            response = make_response(jsonify(pregnancies), 200)
            return response


class PreviousPregnancyForProvider(Resource):
    def get(self, id):
        pregnancies = [
            p.to_dict()
            for p in Present_pregnancy.query.filter_by(
                provider_id=id, is_delivered=True
            ).all()
        ]
        if pregnancies:
            response = make_response(jsonify(pregnancies), 200)
            return response
