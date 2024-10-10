from datetime import timedelta

from flask import jsonify, make_response, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    unset_jwt_cookies,
)
from flask_restful import Resource

from models import Parent, Provider, User


class Home(Resource):
    def get(self):
        return make_response(
            jsonify({"msg": "Welcome to happy hearts api endpoints"}), 200
        )


class Login(Resource):
    def post(self):
        data = request.json
        if not data:
            return {"msg": "No Input was provided"}

        email = data["email"]
        password = data["password"]
        account_type = data["account_type"]

        # Query based on account type
        if account_type == "user":
            user = User.query.filter_by(email=email).first()
        elif account_type == "provider":
            user = Provider.query.filter_by(email=email).first()
        elif account_type == "parent":
            user = Parent.query.filter_by(email=email).first()
        else:
            return make_response(jsonify({"msg": "Invalid account type"}), 400)

        if not user:
            return make_response(jsonify({"msg": "Account doesn't exist"}), 404)

        elif user and user.check_password(password):
            if isinstance(user, User):
                user_id = user.user_id
            elif isinstance(user, Provider):
                user_id = user.provider_id
            elif isinstance(user, Parent):
                user_id = user.parent_id
            else:
                return make_response(jsonify({"msg": "Unknown user type"}), 500)
            print(f"email{user.email},role:{user.role} ,id:{user_id}")
            token = create_access_token(
                identity={
                    "email": user.email,
                    "role": user.role,
                    "id": user_id,
                },
                expires_delta=timedelta(hours=6),
            )

            response = {
                "token": token,
                "role": user.role,
                "id": user_id,
            }
            print(user.email, user.role, user_id)
            return response
        return make_response(jsonify({"msg": "Invalid credentials - password"}), 401)


class Logout(Resource):
    @jwt_required()
    def delete(self):
        current_user = get_jwt_identity()
        response = make_response(
            jsonify({"msg": f"Logged out {current_user.get('email')}"}), 200
        )
        unset_jwt_cookies(response)
        return response
