from flask import jsonify, make_response, request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import db
from models import Medicine


class MedicineAPI(Resource):
    def get(self, id=None):
        if id is None:
            medicines = Medicine.query.all()
            medicine_list = [medicine.to_dict() for medicine in medicines]
            return make_response(jsonify(medicine_list), 200)
        else:
            medicine = Medicine.query.get(id)
            if not medicine:
                return make_response(jsonify({"msg": "Medicine not found"}), 404)
            return make_response(jsonify(medicine.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input data provided"}), 400)

        try:
            medicine = Medicine(
                name=data.get("name"),
                composition=data.get("composition"),
                dosage=data.get("dosage"),
                indication=data.get("indication"),
                side_effects=data.get("side_effects", []),
            )
            db.session.add(medicine)
            db.session.commit()
            return make_response(jsonify({"msg": "Medicine created successfully"}), 201)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self, id):
        medicine = Medicine.query.get(id)
        if not medicine:
            return make_response(jsonify({"msg": "Medicine not found"}), 404)

        data = request.json
        try:
            for key, value in data.items():
                if hasattr(medicine, key):
                    setattr(medicine, key, value)

            db.session.commit()
            return make_response(jsonify({"msg": "Medicine updated successfully"}), 200)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        medicine = Medicine.query.get(id)
        if not medicine:
            return make_response(jsonify({"msg": "Medicine not found"}), 404)

        try:
            db.session.delete(medicine)
            db.session.commit()
            return make_response(jsonify({"msg": "Medicine deleted successfully"}), 200)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)
