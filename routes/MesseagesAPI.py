from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Message, User, Parent, Provider
from config import db
from sqlalchemy.exc import IntegrityError


class MessageAPI(Resource):
    def get(self, id=None):
        if id is None:
            messages = [m.to_dict() for m in Message.query.all()]
            return make_response(jsonify(messages), 200)
        else:
            message = Message.query.filter_by(message_id=id).first()
            if not message:
                return make_response(jsonify({"msg": "Message not found"}), 404)
            return make_response(jsonify(message.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        # Handle optional fields for guest users
        user_id = data.get("user_id")
        parent_id = data.get("parent_id")
        provider_id = data.get("provider_id")

        parent = Parent.query.filter_by(parent_id=parent_id).first()
        provider = Provider.query.filter_by(provider_id=provider_id).first()
        user = User.query.filter_by(user_id=user_id).first()

        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)

        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)
        if not user:
            return make_response(jsonify({"msg": "user not found"}), 404)

        try:
            message = Message(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                email=data.get("email"),
                message=data["message"],
                user_id=user_id,
                parent_id=parent_id,
                provider_id=provider_id,
            )
            db.session.add(message)
            db.session.commit()
            return make_response(jsonify({"msg": "Message created successfully"}), 201)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)
        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self, id):
        data = request.json
        if not data:
            return jsonify({"msg": "No input provided"})

        message = Message.query.filter_by(message_id=id).first()
        if not message:
            return jsonify({"msg": "Message not found"})

        try:
            for field, value in data.items():
                if hasattr(message, field):
                    setattr(message, field, value)
            db.session.commit()
            return make_response(jsonify({"msg": "Message updated successfully"}), 200)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)
        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        message = Message.query.filter_by(message_id=id).first()

        if not message:
            return jsonify({"msg": "Message not found"})
        db.session.delete(message)
        db.session.commit()

        return make_response(jsonify({"msg": "Message deleted successfully"}), 200)


# To register this resource in your API, you'd do something like:
# api.add_resource(MessageAPI, '/messages', '/messages/<int:id>')
