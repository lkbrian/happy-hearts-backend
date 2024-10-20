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
            return make_response(jsonify({"msg": "No input data provided"}), 400)

        parent_id = data.get("parent_id")
        child_id = data.get("child_id")
        national_id = data.get("national_id")
        child_certificate_no = data.get("child_certificate_no")
        test_date_str = data.get("test_date")

        test_date = datetime.strptime(test_date_str.strip(), "%Y-%m-%d")

        if (child_certificate_no or child_id) and (parent_id or national_id):
            return make_response(
                jsonify({"msg": "labtest belongs to parent or child can't be both"}),
                400,
            )

        elif child_certificate_no or child_id:

            child = (
                Child.query.filter_by(certificate_No=child_certificate_no).first()
                or Child.query.filter_by(child_id=child_id).first()
            )
            if not child:
                return make_response(jsonify({"msg": "Child not found"}), 404)

            try:
                lab_test = LabTest(
                    test_name=data.get("test_name"),
                    test_date=test_date,
                    result=data.get("result"),
                    remarks=data.get("remarks"),
                    child_id=child.child_id,
                    parent_id=None,
                )
                db.session.add(lab_test)
                db.session.commit()
                return make_response(
                    jsonify({"msg": "Lab test for child created successfully"}), 201
                )

            except IntegrityError:
                db.session.rollback()
                return make_response(
                    jsonify({"msg": "Integrity constraint failed"}), 400
                )

            except Exception as e:
                return make_response(jsonify({"msg": str(e)}), 500)

        elif parent_id or national_id:
            parent = (
                Parent.query.filter_by(parent_id=parent_id).first()
                or Parent.query.filter_by(national_id=national_id).first()
            )
            if not parent:
                return make_response(jsonify({"msg": "Parent not found"}), 404)
            try:
                lab_test = LabTest(
                    test_name=data.get("test_name"),
                    test_date=test_date,
                    result=data.get("result"),
                    remarks=data.get("remarks"),
                    parent_id=parent.parent_id,
                    child_id=None,
                )
                db.session.add(lab_test)
                db.session.commit()
                return make_response(
                    jsonify({"msg": "Lab test for parent created successfully"}), 201
                )

            except IntegrityError:
                db.session.rollback()
                return make_response(
                    jsonify({"msg": "Integrity constraint failed"}), 400
                )

            except Exception as e:
                return make_response(jsonify({"msg": str(e)}), 500)

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
        else:
            return make_response(jsonify({"msg": "Parent has no labtests"}), 404)


class LabTestsForProviders(Resource):
    def get(self, id):
        labtests = [a.to_dict() for a in LabTest.query.filter_by(providers_id=id).all()]
        if labtests:
            response = make_response(jsonify(labtests), 200)
            return response
        else:
            return make_response(jsonify({"msg": "Providers has no labtests"}), 404)


class LabTestsForChild(Resource):
    def get(self, id):
        labtests = [a.to_dict() for a in LabTest.query.filter_by(child_id=id).all()]
        if labtests:
            response = make_response(jsonify(labtests), 200)
            return response
        else:
            return make_response(jsonify({"msg": "Child has no labtests"}), 404)
