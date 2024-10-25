from flask import make_response, jsonify, request
from flask_restful import Resource
from config import db
from utils.Age import calculate_age
from models import Child, Parent, Document
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
import cloudinary


class ChildrenAPI(Resource):
    def get(self, id=None):
        if id is None:
            children = [c.to_dict() for c in Child.query.all()]
            response = make_response(jsonify(children), 200)
            return response
        else:
            child = Child.query.filter_by(child_id=id).first()
            if not child:
                return make_response(jsonify({"msg": "Child doesn't exist"}), 404)
            response = jsonify(child.to_dict())
            return make_response(response, 200)

    def post(self):
        data = request.form  # Use form for both data and file
        file = request.files.get("media")
        # data = request.json
        if not data:
            return jsonify({"msg": "No input was provided"})
        if not file:
            return jsonify({"msg": "file wasn't was provided"})
        # age calculation
        date_of_birth = data["date_of_birth"]

        age = calculate_age(date_of_birth)
        dob = datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()
        if dob > date.today():
            return make_response(jsonify({"msg": "Enter a past date or today"}), 400)
        existing_child = Child.query.filter_by(
            certificate_No=data.get("certificate_No")
        ).first()
        if existing_child:
            print("Existing child found:", existing_child)
            return make_response(
                jsonify({"msg": "Child with that certificate number exists"}), 404
            )
        parent = Parent.query.get(data.get("parent_id"))
        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)
        try:
            # Upload the passport image to Cloudinary
            upload_result = cloudinary.uploader.upload(file, folder="happyhearts")

            # Create the child record with the Cloudinary link for the passport
            child = Child(
                fullname=data.get("fullname"),
                certificate_No=data.get("certificate_No"),
                date_of_birth=dob,
                age=age,
                gender=data.get("gender"),
                parent_id=data.get("parent_id"),
            )
            db.session.add(child)
            db.session.commit()
            document = Document(
                entityType="child_passport",  # Assuming document type for child passport
                documentType=upload_result["format"],  # e.g., jpg, png
                fileName=file.name,
                size=upload_result["bytes"],
                url=upload_result["secure_url"],  # Cloudinary link
                parent_id=data.get(
                    "parent_id"
                ),  # Assuming the document also belongs to the parent
                child_id=child.child_id,
            )
            db.session.add(document)
            # print(upload_result)
            db.session.commit()
            return make_response(jsonify({"msg": "Child created successfully!"}), 200)
        except IntegrityError as err:
            db.session.rollback()
            response = make_response(
                jsonify({"msg": "Integrity constraint failed"}), 400
            )
            print(err)
            return response
        except Exception as e:
            print(e)
            return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self, id):
        # querying to find the child object to update
        child = Child.query.filter_by(child_id=id).first()
        if not child:
            return make_response(jsonify({"msg": "Child doesn't exist"}), 500)

        data = request.json
        if not data:
            return jsonify({"msg": "No input was provided"})
        # updating the child object
        try:
            for field, value in data.items():
                if hasattr(child, field):
                    if field == "parent_id":
                        parent = Parent.query.get(data.get("parent_id"))
                        if not parent:
                            return make_response(
                                jsonify({"msg": "Parent not found"}), 404
                            )
                    setattr(child, field, value)
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

    def delete(self, id):
        child = Child.query.filter_by(child_id=id).first()
        if not child:
            return make_response(jsonify({"msg": "Child doesn't exist"}), 500)

        db.session.delete(child)
        db.session.commit()
        return make_response(
            jsonify({"msg": "The child has been deleted succesfully"}), 200
        )


class ChildByParentIdAPI(Resource):
    def get(self, id):
        children = Child.query.filter(Child.parent_id == id).all()
        if children:
            children_list = [child.to_dict() for child in children]
            return make_response(jsonify(children_list), 200)
