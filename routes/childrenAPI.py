from flask import make_response, jsonify, request
from flask_restful import Resource
from config import db
from utils.Age import  calculate_age
from models import Child,Parent
from sqlalchemy.exc import IntegrityError
from datetime import datetime,date


class ChildrenAPI(Resource):
    def get(self,id=None):
        if id is None:
            children = [c.to_dict() for c in Child.query.all()]
            response = make_response(jsonify(children),200)
            return response
        else:
            child = Child.query.filter_by(child_id=id).first()
            if not child:
                return make_response(jsonify({"msg":"Child doesn't exist"}),404)
            response = jsonify(child.to_dict())
            return make_response(response,200)

    def post(self):
        # get data required
        data = request.json
        if not data:
            return jsonify({"msg":"No input was provided"})
        # age calculation
        date_of_birth = data['date_of_birth']

        age= calculate_age(date_of_birth)
        dob = datetime.strptime(data["date_of_birth"], "%Y/%m/%d").date()
        if dob > date.today():
            return make_response(
                jsonify({"msg": "Enter a past date or today"}), 400
            )
        parent = Parent.query.get(data.get("parent_id"))
        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)
        try:
            child = Child(
            fullname=data["fullname"],
            certificate_No=data["certificate_No"],
            date_of_birth=dob,
            age=age,
            gender=data["gender"],
            passport=data["passport"],
            parent_id=data["parent_id"],
            )
            db.session.add(child)
            db.session.commit()
            response= make_response(jsonify({"msg":"Child created sucessfully"}),201)
            return response
        except IntegrityError:
            db.session.rollback()
            response=make_response(jsonify({"msg":"Integrity constraint failed"}),400)
            return response
        except Exception as e:
            return make_response(jsonify({"msg":str(e)}),500)

    def patch(self,id):
        # querying to find the child object to update
        child = Child.query.filter_by(child_id=id).first()
        if not child:
            return make_response(jsonify({"msg":"Child doesn't exist"}),500)

        data = request.json
        if not data:
            return jsonify({"msg": "No input was provided"})
        # updating the child object
        try:
            for field,value in data.items():
                if hasattr(child,field):
                    if field =="parent_id":
                        parent = Parent.query.get(data.get("parent_id"))
                        if not parent:
                            return make_response(jsonify({"msg": "Parent not found"}), 404)
                    setattr(child,field,value)
            db.session.commit()
            return make_response(jsonify({"msg": "updating child sucessful"}), 200)

        # lookout for errors
        except IntegrityError:
            db.session.rollback()
            return make_response(
                jsonify({"msg": "Integrity constraint failed, update unsuccesful"}),
                400,
            )

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

    def delete(self,id):
        child = Child.query.filter_by(child_id=id).first()
        if not child:
            return make_response(jsonify({"msg": "Child doesn't exist"}), 500)

        db.session.delete(child)
        db.session.commit()
        return make_response(jsonify({"msg":"The child has been deleted succesfully"}),200)
