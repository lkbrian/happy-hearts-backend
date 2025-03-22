from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Room
from config import db
from sqlalchemy.exc import IntegrityError


class RoomAPI(Resource):
    def get(self, id=None):
        if id is None:
            rooms = [r.to_dict() for r in Room.query.all()]
            return make_response(jsonify(rooms), 200)
        else:
            room = Room.query.filter_by(room_id=id).first()
            if not room:
                return make_response(jsonify({"msg": "Room not found"}), 404)
            return make_response(jsonify(room.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        try:
            room = Room(
                room_number=data["room_number"],
                capacity=data["capacity"],
                room_type=data["room_type"],
                facilities=data.get("facilities"),
                location=data.get("location"),
                notes=data.get("notes"),
            )
            db.session.add(room)
            db.session.commit()

            return make_response(jsonify({"msg": "Room created successfully"}), 201)

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

        room = Room.query.filter_by(room_id=id).first()
        if not room:
            return jsonify({"msg": "Room not found"})

        try:
            for field, value in data.items():
                if hasattr(room, field):
                    setattr(room, field, value)
            db.session.commit()
            return make_response(jsonify({"msg": "Room updated successfully"}), 200)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        room = Room.query.filter_by(room_id=id).first()

        if not room:
            return jsonify({"msg": "Room not found"})
        db.session.delete(room)
        db.session.commit()

        return make_response(jsonify({"msg": "Room deleted successfully"}), 200)


class AvailableRooms(Resource):
    def get(self):
        rooms = [
            room.to_dict() for room in Room.query.filter_by(status="Available").all()
        ]
        if not rooms:
            return make_response(jsonify({"msg": "Room not found"}), 404)
        return make_response(jsonify(rooms), 200)
