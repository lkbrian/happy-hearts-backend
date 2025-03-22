from flask import make_response, request, jsonify
from flask_restful import Resource
from config import db
from models import Payment, Parent


class PaymentAPI(Resource):

    def get(self, payment_id=None):
        if payment_id:
            payment = Payment.query.filter_by(payment_id=payment_id).first()
            if not payment:
                return make_response(jsonify({"msg": "Payment not found"}), 404)
            return make_response(jsonify(payment.to_dict()), 200)
        else:
            payments = Payment.query.all()
            return jsonify([payment.to_dict() for payment in payments])

    # POST method to create a new payment
    def post(self):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        parent_id = data.get("parent_id")
        amount = data.get("amount")
        payment_method = data.get("payment_method")

        if not parent_id or not amount or not payment_method:
            return make_response(jsonify({"msg": "Missing fields"}), 400)

        try:
            parent = Parent.query.filter_by(parent_id=parent_id).first()
            if not parent:
                return make_response(jsonify({"msg": "Parent not found"}), 404)

            payment = Payment(
                parent_id=parent_id, amount=amount, payment_method=payment_method
            )

            db.session.add(payment)
            db.session.commit()

            return make_response(jsonify({ "msg": "Payment created successfully","payment": payment.to_dict()},201))

        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"msg": str(e)}), 500)

    def patch(self, id):
        data = request.json
        if not data:
            return make_response(jsonify({"msg": "No input provided"}), 400)

        payment = Payment.query.filter_by(payment_id=id).first()
        if not payment:
            return make_response(jsonify({"msg": "Payment not found"}), 404)

        parent = Parent.query.filter_by(parent_id=id).first()
        if not parent:
            return make_response(jsonify({"msg": "Parent not found"}), 404)

        if "parent_id" in data:
            payment.parent_id = parent.parent_id
        if "amount" in data:
            payment.amount = data.get("amount")
        if "payment_method" in data:
            payment.payment_method = data.get("payment_method")

        try:
            db.session.commit()
            return make_response(jsonify({"msg": "Payment updated successfully"}), 200)

        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": str(e)}), 500

    def delete(self, id):
        payment = Payment.query.filter_by(payment_id=id).first()
        if not payment:
            return make_response(jsonify({"msg": "Payment not found"}), 404)

        try:
            db.session.delete(payment)
            db.session.commit()
            return make_response(jsonify({"msg": "Payment deleted successfully"}), 200)

        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"msg": str(e)}), 500)
