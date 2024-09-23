from config import db
from flask_restful import Resource
from models import Appointment,Provider,Parent
from flask import make_response,jsonify, request
from sqlalchemy.exc import IntegrityError
from datetime import date,datetime

class appointmentsAPI(Resource):
    def get(self,id=None):
        if id is None:
            appointments= [a.to_dict() for a in Appointment.query.all()]
            response = make_response(jsonify(appointments),200)
            return response
        else :
            appointment = Appointment.query.filter_by(parent_id=id).first()
            response = make_response(jsonify(appointment),200)
            return response

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)
        appointment_date = datetime.strptime(data["appointment_date"], "%Y-%m-%d %H:%M").date()
        if appointment_date < date.today():
            return make_response(jsonify({"msg":"Enter a date later than today or today"}),400)
        
        parent = Parent.query.get(data.get("parent_id"))
        provider = Provider.query.get(data.get("provider_id"))

        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)

        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)
        try:
            appointment = Appointment(
                parent_id=data['parent_id'],
                provider_id=data['provider_id'],
                reason=data['reason'],
                appointment_date=appointment_date,
            )
            db.session.add(appointment)
            db.session.commit()
            return make_response(jsonify({"msg": "Appointment created successfully"}), 201)

        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def patch(self,id):
        data=request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        appointment = Appointment.query.filter_by(id=id).first()
        if not appointment:
            return make_response(jsonify({"msg":"Appointment doesn't exist"}),404)

        try:
            for field,value in data.items():
                if field == "appointment_date":  # Handle date conversion
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d %H:%M")
                    except ValueError:
                        return make_response(jsonify({"msg": f"Invalid date format for {field}, should be YYYY-MM-DD"}),400,)

                elif field == "parent_id":
                    parent = Parent.query.get(data.get("parent_id"))                        
                    if not parent:
                        return make_response(jsonify({"msg": "Parent not found"}), 404)
                    
                elif field == "provider_id":
                    provider = Provider.query.get(data.get("provider_id"))
                    if not provider:
                        return make_response(jsonify({"msg": "Provider not found"}), 404)
                if hasattr(appointment,field):
                    setattr(appointment, field, value)
            db.session.commit()
            return make_response(jsonify({"msg":"Appointment updated succesfully"}),201)
        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def delete(self,id):
        appointment = Appointment.query.filter_by(appointment_id=id).first()
        if not appointment:
            return make_response(jsonify({"msg":"Appointment doesn't exist"}),404)
        db.session.delete(appointment)
        return make_response(jsonify({"msg":"Appointment deleted sucesfully"}),200)
