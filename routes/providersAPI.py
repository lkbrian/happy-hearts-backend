from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Provider
from models import User
from config import db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

class providersAPI(Resource):
    def get(self,id=None):
        if id is None:            
            providers= [p.to_dict() for p in Provider.query.all()]
            response = make_response(jsonify(providers),200)
            return response
        else :
            user = User.query.get_or_404(id)
        if user.role != "provider":
            return {"message": "User is not a provider"}, 400

        provider = Provider.query.filter_by(parent_id=id).first()
        response = make_response(jsonify(provider),200)
        return response

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        try:
            provider = Provider(
                name=data['name'],
                email=data['email'],
                national_id=data['national_id'],
                phone_number=data['phone_number'],
                gender=data['gender'],
                passport=data['passport'],
                password_hash=generate_password_hash(data['password'], method="pbkdf2:sha512"),
            )

            db.session.add(provider)
            db.session.commit()

            return make_response(jsonify({"msg": "Provider created successfully"}), 201)

        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({"msg": "Integrity constraint failed"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self,id):
        data = request.json
        if not data:
            return jsonify({"msg": "No Input was provided"})

        provider = Provider.query.filter_by(parent_id=id).first()
        if not provider:
            return jsonify({"msg":"Provider doesn't exist"})

        try:
            for field,value in data.items():
                if hasattr(provider,field):
                    setattr(provider,field,value)
            db.session.commit()
            response = make_response(jsonify({"msg":"Provider updated succesfully"}))
        except IntegrityError:
            db.session.rollback()
            response = make_response(
                jsonify({"msg": "Integrity constraint failed"}), 400
            )
            return response
        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self,id):
        provider = Provider.query.filter_by(parent_id=id).first()

        if not provider:
            return jsonify({"msg":"Provider doesn't exist"})
        db.session.delete(provider)
        db.session.commit()

        response = make_response(jsonify({"msg":"Provider deletd succesfully"}),200) 
        return response
