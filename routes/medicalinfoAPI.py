from flask_restful import Resource
from flask import request, jsonify, make_response
from models import Medical_info_parent,Parent
from config import db
from sqlalchemy.exc import IntegrityError
# from datetime import datetime

class MedicalInfoParentAPI(Resource):
    def get(self, id=None):
        if id is None:
            medical_info = [info.to_dict() for info in Medical_info_parent.query.all()]
            return make_response(jsonify(medical_info), 200)
        else:
            info = Medical_info_parent.query.filter_by(history_id=id).first()
            if not info:
                return jsonify({"msg": "Medical info not found"}), 404
            return make_response(jsonify(info.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)
        
        national_id = data["national_id"]
        parent = Parent.query.filter_by(national_id=national_id).first()
        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)

        try:
            info = Medical_info_parent(
                blood_transfusion=data.get("blood_transfusion"),
                family_history=data.get("family_history"),
                twins=data.get("twins"),
                tuberclosis=data.get("tuberclosis"),
                diabetes=data.get("diabetes"),
                hypertension=data.get("hypertension"),
                parent_id=parent.parent_id,
            )
            db.session.add(info)
            db.session.commit()
            return make_response(jsonify({"msg": "Medical info created successfully"}), 201)

        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def patch(self, id):
        data = request.json
        if not data:
            return jsonify({"msg": "No input provided"})

        info = Medical_info_parent.query.filter_by(history_id=id).first()
        if not info:
            return jsonify({"msg": "Medical info not found"})

        try:
            for field, value in data.items():
                if hasattr(info, field):
                    setattr(info, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Medical info updated successfully"}), 200
            )

        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def delete(self, id):
        info = Medical_info_parent.query.filter_by(history_id=id).first()
        if not info:
            return jsonify({"msg": "Medical info not found"})
        db.session.delete(info)
        db.session.commit()
        return make_response(jsonify({"msg": "Medical info deleted successfully"}), 200)
