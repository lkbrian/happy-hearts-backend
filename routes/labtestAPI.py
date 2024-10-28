from datetime import datetime

from config import db
from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Child, LabTest, Parent
from sqlalchemy.exc import IntegrityError


class LabTestAPI(Resource):

    def get(self, id=None):
        if id is None:
            lab_tests = LabTest.query.all()
            lab_test_list = [lab_test.to_dict() for lab_test in lab_tests]
            return make_response(jsonify(lab_test_list), 200)
        else:
            lab_test = LabTest.query.get(id)
            if not lab_test:
                return make_response(jsonify({"msg": "Lab test not found"}), 404)
            return make_response(jsonify(lab_test.to_dict()), 200)

    def post(self):
        data = request.json
        if not data:
            return make_json_response("No input data provided", 400)

        validation_result = find_parent_or_child(
            parent_id=data.get("parent_id"),
            child_certificate_no=data.get("child_certificate_no"),
        )

        if validation_result is None:
            return make_json_response(
                "Lab test must belong to either parent or child, not both", 400
            )

        try:
            test_date = datetime.strptime(data["test_date"], "%Y-%m-%d")
            lab_test = LabTest(
                test_name=data["test_name"],
                test_date=test_date,
                result=data["result"],
                remarks=data.get("remarks"),
                parent_id=validation_result.get("parent", {}).get("parent_id"),
                child_id=validation_result.get("child", {}).get("child_id"),
            )
            db.session.add(lab_test)
            db.session.commit()
            return make_json_response("Lab test created successfully", 201)

        except IntegrityError:
            db.session.rollback()
            return make_json_response("Integrity constraint failed", 400)

        except Exception as e:
            return make_json_response(str(e), 500)

    def patch(self, id):
        lab_test = LabTest.query.get(id)
        if not lab_test:
            return make_response(jsonify({"msg": "Lab test not found"}), 404)

        data = request.json
        try:
            for key, value in data.items():
                if key == "test_date":
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        return make_response(
                            jsonify({"msg": "Invalid date format. Use YYYY-MM-DD"}), 400
                        )

                if key in ["parent_id", "national_id"]:
                    parent = (
                        Parent.query.filter_by(parent_id=data.get("parent_id")).first()
                        or Parent.query.filter_by(
                            national_id=data.get("national_id")
                        ).first()
                    )

                    if not parent:
                        return make_response(jsonify({"msg": "Parent not found"}), 404)
                    else:
                        value = parent.parent_id

                elif key == "child_certificate_no":
                    child = Child.query.filter_by(certificate_No=value).first()
                    if not child:
                        return make_response(jsonify({"msg": "Child not found"}), 404)
                    else:
                        value = child.child_id

                if hasattr(lab_test, key):
                    setattr(lab_test, key, value)

            db.session.commit()
            return make_response(jsonify({"msg": "Lab test updated successfully"}), 200)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    # DELETE a lab test by ID
    def delete(self, id):
        lab_test = LabTest.query.get(id)
        if not lab_test:
            return make_response(jsonify({"msg": "Lab test not found"}), 404)

        try:
            db.session.delete(lab_test)
            db.session.commit()
            return make_response(jsonify({"msg": "Lab test deleted successfully"}), 200)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)


class LabTestsForParents(Resource):
    def get(self, id):
        labtests = [a.to_dict() for a in LabTest.query.filter_by(parent_id=id).all()]
        if labtests:
            response = make_response(jsonify(labtests), 200)
            return response


class LabTestsForProviders(Resource):
    def get(self, id):
        labtests = [a.to_dict() for a in LabTest.query.filter_by(provider_id=id).all()]
        if labtests:
            response = make_response(jsonify(labtests), 200)
            return response


class LabTestsForChild(Resource):
    def get(self, id):
        labtests = [a.to_dict() for a in LabTest.query.filter_by(child_id=id).all()]
        if labtests:
            response = make_response(jsonify(labtests), 200)
            return response


def find_parent_or_child(parent_id=None, child_certificate_no=None):
    if parent_id:
        parent = Parent.query.get(parent_id)
        if parent:
            return {"parent": parent}
    elif child_certificate_no:
        child = Child.query.filter_by(certificate_No=child_certificate_no).first()
        if child:
            return {"child": child}
    return None


def make_json_response(message, status_code=200):
    return make_response(jsonify({"msg": message}), status_code)
