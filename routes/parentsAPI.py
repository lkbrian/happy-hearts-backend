from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Parent
from config import db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash


class parentsAPI(Resource):
    def get(self, id=None):
        if id is None:
            parents = [p.to_dict() for p in Parent.query.all()]
            response = make_response(jsonify(parents), 200)
            return response
        else:
            parent = Parent.query.filter_by(parent_id=id).first()
            if parent:
                response = make_response(jsonify(parent.to_dict()), 200)
                return response
            else:
                return make_response(jsonify({"msg": "Parent not found"}), 404)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        email = data["email"]
        parent = Parent.query.filter_by(email=email).first()
        if parent:
            return make_response(jsonify({"msg": "Parent already registered"}), 400)

        try:
            parent = Parent(
                name=data["name"],
                email=data["email"],
                national_id=data["national_id"],
                phone_number=data["phone_number"],
                gender=data["gender"],
                password_hash=generate_password_hash(
                    data["password"], method="pbkdf2:sha512"
                ),
            )

            db.session.add(parent)
            db.session.commit()

            return make_response(jsonify({"msg": "Parent created successfully"}), 201)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self, id):
        data = request.json
        if not data:
            return jsonify({"msg": "No Input was provided"})

        parent = Parent.query.filter_by(parent_id=id).first()
        if not parent:
            return jsonify({"msg": "Parent doesn't exist"})

        try:
            for field, value in data.items():
                if hasattr(parent, field):
                    setattr(parent, field, value)
            db.session.commit()
            response = make_response(
                jsonify({"msg": "Parent updated succesfully"}), 200
            )
        except IntegrityError:
            db.session.rollback()
            response = make_response(
                jsonify({"msg": "Integrity constraint failed"}), 400
            )
            return response
        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        parent = Parent.query.filter_by(parent_id=id).first()

        if not parent:
            return jsonify({"msg": "Parent doesn't exist"})
        db.session.delete(parent)
        db.session.commit()

        response = make_response(jsonify({"msg": "Parent deletd succesfully"}), 200)
        return response
