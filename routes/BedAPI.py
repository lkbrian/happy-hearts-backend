from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Bed, Room
from config import db
from sqlalchemy.exc import IntegrityError


class BedAPI(Resource):
    def get(self, id=None):
        if id is None:
            beds = [b.to_dict() for b in Bed.query.all()]
            return make_response(jsonify(beds), 200)
        else:
            bed = Bed.query.filter_by(bed_id=id).first()
            if not bed:
                return make_response(jsonify({"msg": "Bed not found"}), 404)
            return make_response(jsonify(bed.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        room_id = data.get("room_id")
        room = Room.query.get(room_id)
        if not room:
            return make_response(jsonify({"msg": "Room not found"}), 404)

        current_bed_occupancy = int(room.current_bed_occupancy)
        capacity = int(room.capacity)

        if current_bed_occupancy >= capacity:
            return make_response(
                jsonify({"msg": "Room is full can't assign a bed"}), 404
            )

        try:
            bed = Bed(
                bed_number=data["bed_number"],
                bed_type=data["bed_type"],
                room_id=room_id,
            )
            db.session.add(bed)
            room.current_bed_occupancy += 1
            db.session.commit()
            room.status = (
                "Full"
                if room.current_occupancy == room.current_bed_occupancy
                else "Available"
            )
            db.session.commit()

            return make_response(jsonify({"msg": "Bed created successfully"}), 201)

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

        bed = Bed.query.filter_by(bed_id=id).first()
        if not bed:
            return jsonify({"msg": "Bed not found"})

        try:
            for field, value in data.items():
                if hasattr(bed, field):
                    setattr(bed, field, value)
            db.session.commit()
            return make_response(jsonify({"msg": "Bed updated successfully"}), 200)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        bed = Bed.query.filter_by(bed_id=id).first()

        if not bed:
            return jsonify({"msg": "Bed not found"})
        db.session.delete(bed)
        db.session.commit()

        return make_response(jsonify({"msg": "Bed deleted successfully"}), 200)


class AvailableBedsForRoom(Resource):
    def get(self, id):
        beds = [
            b.to_dict()
            for b in Bed.query.filter_by(room_id=id, is_occupied=False).all()
        ]
        if not beds:
            return make_response(jsonify({"msg": "Bed are not available"}), 404)
        return make_response(jsonify(beds), 200)
