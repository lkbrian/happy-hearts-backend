from flask_restful import Resource
from models import Vaccine
from flask import make_response,jsonify, request
from config import db
from sqlalchemy.exc import IntegrityError

class vaccinesAPI(Resource):
    def get(self,id=None):
        if id is None:
            vaccines=[v.to_dict() for v in Vaccine.query.all()]
            return make_response(jsonify(vaccines),200)
        else:
            vaccine=Vaccine.query.filter_by(id=id).first()
            if not vaccine:
                return make_response(jsonify({"msg": "Vaccine doesn't exist"}), 404)

            return make_response(jsonify(vaccine.to_dict()),200)

        def post(self):
            data = request.json
            if not data:
                return make_response(jsonify({"msg": "No input provided"}), 400)

            try:
                vaccine = Vaccine(
                    name=data["name"],
                    composition=data["composition"],
                    schedule=data["schedule"],
                    indication=data["indication"],
                    side_effects=data["side_effects"],
                    info=data["additional_information"],
                )

                db.session.add(vaccine)
                db.session.commit()

                return make_response(jsonify({"msg": "Vaccine created successfully"}), 201)

            except IntegrityError:
                db.session.rollback()
                return jsonify({"msg": "Integrity constraint failed"}), 400

            except Exception as e:
                return jsonify({"msg": str(e)}), 500

    def patch(self,id):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        vaccine = Vaccine.query.filter_by(id=id).first()
        if not vaccine:
            return make_response(jsonify({"msg":"Vaccine doesn't exist"}),404)

        try:
            for field,value in data.items():
                if hasattr(vaccine,field):
                    setattr(vaccine,field,value)
            db.session.commit()
            return make_response(jsonify({"msg": "Vaccine updated succesfully"}), 200)            
        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def delete(self,id):
        vaccine = Vaccine.query.filter_by(id=id).first()
        if not vaccine:
            return make_response(jsonify({"msg": "Vaccine doesn't exist"}), 404)
        
        db.session.delete(vaccine)
        db.session.commit()
        return make_response(jsonify({"msg":"Vaccine deleted succesfully"}),200)
