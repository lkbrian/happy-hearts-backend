from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Admission, Parent, Child, Provider, Room, Bed
from config import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime


class AdmissionAPI(Resource):
    def get(self, id=None):
        if id is None:
            admissions = [a.to_dict() for a in Admission.query.all()]
            return make_response(jsonify(admissions), 200)
        else:
            admission = Admission.query.filter_by(admission_id=id).first()
            if not admission:
                return make_response(jsonify({"msg": "Admission not found"}), 404)
            return make_response(jsonify(admission.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        national_id = data.get("national_id")
        parent_id = data.get("parent_id")
        provider_id = data.get("provider_id")
        child_id = data.get("child_id")
        room_id = data.get("room_id")
        certificate_No = data.get("certificate_No")
        bed_id = data.get("bed_id")

        parent = (
            Parent.query.filter_by(national_id=national_id).first()
            or Parent.query.filter_by(parent_id=parent_id).first()
        )
        provider = Provider.query.filter_by(provider_id=provider_id).first()
        child = (
            Child.query.filter_by(certificate_No=certificate_No).first()
            or Child.query.filter_by(child_id=child_id).first()
        )
        print(child)
        if child_id and not child:
            return make_response(jsonify({"msg": "Child not found"}), 404)
        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)
        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)

        # Check if the room exists and if it has available capacity
        room = Room.query.get(room_id)
        if not room:
            return make_response(jsonify({"msg": "Room not found"}), 404)

        if room.current_occupancy >= room.capacity:
            return make_response(jsonify({"msg": "Room is at full capacity"}), 400)

        # Check if the bed exists
        bed = Bed.query.get(bed_id)
        if not bed:
            return make_response(jsonify({"msg": "Bed not found"}), 404)

        # Assuming you have logic to get the bed details
        bed = Bed.query.filter_by(room_id=room.room_id, is_occupied=False).first()
        if not bed:
            return make_response(
                jsonify({"msg": "No available beds in this room"}), 404
            )

        try:
            admission = Admission(
                admission_date=datetime.strptime(
                    data["admission_date"], "%Y-%m-%dT%H:%M"
                ),
                parent_id=parent.parent_id,
                provider_id=data.get("provider_id"),
                child_id=child.child_id if child else None,
                reason_for_admission=data["reason_for_admission"],
                general_assessment=data.get("general_assessment"),
                initial_treatment_plan=data.get("initial_treatment_plan"),
                room_id=room.room_id,
                insurance_details=data.get("insurance_details"),
                bed_id=bed.bed_id,  # Assign the bed ID
            )
            db.session.add(admission)

            # Update room and bed status
            room.current_occupancy += 1
            room.is_occupied = room.current_occupancy > 0
            bed.is_occupied = True
            room.status = (
                "Full" if room.current_occupancy == room.capacity else "Available"
            )

            db.session.commit()

            return make_response(
                jsonify({"msg": "Admission created successfully"}), 201
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

        admission = Admission.query.filter_by(admission_id=id).first()
        if not admission:
            return jsonify({"msg": "Admission not found"})

        try:
            for field, value in data.items():
                if field == "parent_id":
                    parent = Parent.query.get(value)
                    if not parent:
                        return make_response(jsonify({"msg": "Parent not found"}), 404)

                elif field == "child_id":
                    child = Child.query.get(value)
                    if child is None:
                        return make_response(jsonify({"msg": "Child not found"}), 404)

                if hasattr(admission, field):
                    setattr(admission, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Admission updated successfully"}), 200
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        admission = Admission.query.filter_by(admission_id=id).first()

        if not admission:
            return jsonify({"msg": "Admission not found"})
        db.session.delete(admission)
        db.session.commit()

        return make_response(jsonify({"msg": "Admission deleted successfully"}), 200)
