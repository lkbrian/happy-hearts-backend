from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Birth, Provider, Parent
from config import db
from sqlalchemy.exc import IntegrityError


class BirthAPI(Resource):
    def get(self, id=None):
        if id is None:
            births = [b.to_dict() for b in Birth.query.all()]
            return make_response(jsonify(births), 200)
        else:
            birth = Birth.query.filter_by(birth_id=id).first()
            if not birth:
                return make_response(jsonify({"msg": "Birth record not found"}), 404)
            return make_response(jsonify(birth.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        provider_id = data.get("provider_id")
        parent_id = data.get("parent_id")

        provider = Provider.query.get(provider_id)
        parent = Parent.query.get(parent_id)

        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)

        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)

        try:
            birth = Birth(
                delivery_id=data["delivery_id"],
                baby_name=data["baby_name"],
                date_of_birth=data["date_of_birth"],
                place_of_birth=data["place_of_birth"],
                weight=data["weight"],
                gender=data["gender"],
                mother_full_name=data["mother_full_name"],
                mother_national_id=data["mother_national_id"],
                mother_age=data.get("mother_age"),
                mother_occupation=data.get("mother_occupation"),
                father_full_name=data.get("father_full_name"),
                father_national_id=data.get("father_national_id"),
                father_age=data.get("father_age"),
                father_occupation=data.get("father_occupation"),
                marital_status=data.get("marital_status"),
                provider_id=provider_id,
                parent_id=parent_id,
            )
            db.session.add(birth)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Birth record created successfully"}), 201
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
            return jsonify({"msg": "No input provided"})

        birth = Birth.query.filter_by(birth_id=id).first()
        if not birth:
            return jsonify({"msg": "Birth record not found"})

        try:
            for field, value in data.items():
                if hasattr(birth, field):
                    setattr(birth, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Birth record updated successfully"}), 200
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f"{error_message}"}), 400)

        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        birth = Birth.query.filter_by(birth_id=id).first()

        if not birth:
            return jsonify({"msg": "Birth record not found"})
        db.session.delete(birth)
        db.session.commit()

        return make_response(jsonify({"msg": "Birth record deleted successfully"}), 200)


class BirthForProvider(Resource):
    def get(self, id):
        births = [a.to_dict() for a in Birth.query.filter_by(provider_id=id).all()]
        if births:
            response = make_response(jsonify(births), 200)
            return response


class BirthForParent(Resource):
    def get(self, id):
        births = [a.to_dict() for a in Birth.query.filter_by(parent_id=id).all()]
        if births:
            response = make_response(jsonify(births), 200)
            return response
