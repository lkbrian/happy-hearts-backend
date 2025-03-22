from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Conversation, Message
from config import db
from sqlalchemy.exc import IntegrityError


class ConversationAPI(Resource):
    def get(self, id=None):
        if id is None:
            conversations = [c.to_dict() for c in Conversation.query.all()]
            return make_response(jsonify(conversations), 200)
        else:
            conversation = Conversation.query.filter_by(conversation_id=id).first()
            if not conversation:
                return make_response(jsonify({"msg": "Conversation not found"}), 404)
            return make_response(jsonify(conversation.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        try:
            # Create a new conversation
            conversation = Conversation()
            db.session.add(conversation)
            db.session.commit()  # Commit to generate conversation_id

            return make_response(
                jsonify(
                    {
                        "msg": "Conversation created successfully",
                        "conversation_id": conversation.conversation_id,
                    }
                ),
                201,
            )

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

        conversation = Conversation.query.filter_by(conversation_id=id).first()
        if not conversation:
            return jsonify({"msg": "Conversation not found"})

        try:
            for field, value in data.items():
                if hasattr(conversation, field):
                    setattr(conversation, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Conversation updated successfully"}), 200
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)
        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        conversation = Conversation.query.filter_by(conversation_id=id).first()

        if not conversation:
            return jsonify({"msg": "Conversation not found"})

        # Optionally delete all associated messages
        Message.query.filter_by(conversation_id=id).delete()

        db.session.delete(conversation)
        db.session.commit()

        return make_response(jsonify({"msg": "Conversation deleted successfully"}), 200)


# To register this resource in your API, you'd do something like:
# api.add_resource(ConversationAPI, '/conversations', '/conversations/<int:id>')
