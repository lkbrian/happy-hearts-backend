from flask import make_response, jsonify, request
from flask_restful import Resource
from config import db, valid_roles
from models import User
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError


class UserAPI(Resource):
    def get(self, id=None):
        if id is None:
            users = [u.to_dict() for u in User.query.all()]
            response = make_response(jsonify(users), 200)
            return response
        else:
            user = User.query.filter_by(user_id=id).first()
            if not user:
                response = make_response(jsonify({"msg": "user not found"}), 404)
                return response
            response = make_response(jsonify(user.to_dict()), 200)
            return response

    def post(self):
        data = request.json

        if not data:
            return {"msg": "No Input was provided"}

        try:
            # get user credentials
            email = data["email"]
            name = data["name"]
            role = data["role"]
            password = data["password"]

            # check for existing users
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return make_response(
                    jsonify({"msg": "User with this email already exists"}), 409
                )

            # create a user if they don't exist
            user = User(
                name=name,
                email=email,
                role=role,
                password_hash=generate_password_hash(password, method="pbkdf2:sha512"),
            )
            db.session.add(user)
            db.session.commit()

            return make_response(
                jsonify({"msg": f"{role} account created sucessfully for {name}"}), 201
            )
        except IntegrityError:
            db.session.rollback()
            return make_response(
                jsonify(
                    {"msg": "Integrity constraint failed, Registration Unsuccesful"}
                ),
                400,
            )

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

    def patch(self, id):
        # ensure id is provided
        if id is None:
            return make_response(jsonify({"msg": "Provide id"}), 400)

        # check that the user is available
        user = User.query.filter_by(user_id=id).first()
        if not user:
            return make_response(jsonify({"msg": "user not found"}), 404)

        # check that the data was provided
        data = request.json
        if not data:
            return {"msg": "No Input was provided"}

        # update the necessary fields
        try:
            for field, value in data.items():
                if field == "role":
                    if value not in valid_roles:
                        return make_response(
                            jsonify({"msg": "Invalid role specified"}), 400
                        )
                    # Update the role only if it's valid
                    user.role = value
                elif field == "email":
                    existing_mail = User.query.filter_by(email=value).first()
                    if existing_mail:
                        return make_response(
                            jsonify({"msg": "a user with this email already exists"}),
                            409,
                        )

                elif hasattr(user, field):
                    setattr(user, field, value)
            db.session.commit()
            return make_response(jsonify({"msg": "updating user sucessful"}), 200)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

    def delete(self, id):
        if id is None:
            return make_response(jsonify({"msg": "Provide id"}), 400)

        # check that the user is available
        user = User.query.filter_by(user_id=id).first()
        if not user:
            return make_response(jsonify({"msg": "user not found"}), 404)

        try:
            # delete the user
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({"msg": "deleted sucessfully"}), 200)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)
