from config import db
from flask_restful import Resource
from models import Record,Child,Parent,Provider,Vaccine
from flask import make_response, jsonify, request
from sqlalchemy.exc import IntegrityError


class RecordsApi(Resource):
    def get(self, id=None):
        if id is None:
            records = [r.to_dict() for r in Record.query.all()]
            response = make_response(jsonify(records), 200)
            return response
        else:
            record = Record.query.filter_by(parent_id=id).first()
            response = make_response(jsonify(record), 200)
            return response

    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        parent_id = data.get("parent_id")
        child_id = data.get("child_id")
        national_id = data.get("national_id")
        child_certificate_no = data.get("child_certificate_no")
        provider_id=data["provider_id"]
        vaccine_id=data["vaccine_id"]

        if not (parent_id or national_id) or not (child_certificate_no or child_id):
            return make_response(jsonify({"msg": "Parent ID and Child Certificate No are required"}), 400)

        parent = (
            Parent.query.filter_by(parent_id=parent_id).first()
            or Parent.query.filter_by(national_id=national_id).first()
        )
        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)

        child = Child.query.filter_by(certificate_No=child_certificate_no).first() or Child.query.filter_by(child_id=child_id).first()
        if not child:
            return make_response(jsonify({"msg": "Child not found"}), 404)

        provider = Provider.query.filter_by(provider_id=provider_id).first()
        if not provider:
            return make_response(jsonify({"msg": "Provider not found"}), 404)

        vaccine = Vaccine.query.filter_by(vaccine_id=vaccine_id).first()
        if not vaccine:
            return make_response(jsonify({"msg": "Vaccine not found"}), 404)

        if child.parent_id != parent.parent_id:
            return make_response(jsonify({"msg": "Child does not belong to the given parent"}), 400)

        try:
            record = Record(
                parent_id=parent.parent_id,
                child_id=child.child_id, 
                provider_id=provider.provider_id,
                vaccine_id=vaccine_id
            )
            db.session.add(record)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Record created successfully"}), 201
            )

        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400

        except Exception as e:
            return jsonify({"msg": str(e)}), 500
    def patch(self, id):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        record = Record.query.filter_by(id=id).first()
        if not record:
            return make_response(jsonify({"msg": "Record doesn't exist"}), 404)

        try:
            for field, value in data.items():

                if field == "parent_id":
                    parent = Parent.query.get(data.get("parent_id"))                        
                    if not parent:
                        return make_response(jsonify({"msg": "Parent not found"}), 404)

                elif field == "provider_id":
                    provider = Provider.query.get(data.get("provider_id"))
                    if not provider:
                        return make_response(jsonify({"msg": "Provider not found"}), 404)   

                elif field == "child_certificate_no":
                    child = Child.query.get(data.get("child_certificate_no"))
                    if not child:
                        return make_response(jsonify({"msg": "Child not found"}), 404)               
                if hasattr(record, field):
                    setattr(record, field, value)
            db.session.commit()
            return make_response(
                jsonify({"msg": "Record updated succesfully"}), 201
            )
        except IntegrityError:
            db.session.rollback()
            return jsonify({"msg": "Integrity constraint failed"}), 400

        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    def delete(self, id):
        record = Record.query.filter_by(id=id).first()
        if not record:
            return make_response(jsonify({"msg": "Record doesn't exist"}), 404)
        db.session.delete(record)
        return make_response(jsonify({"msg": "Record deleted sucesfully"}), 200)
