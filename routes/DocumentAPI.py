from flask import jsonify, make_response, request
from flask_restful import Resource
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from config import db
from models import Document
from datetime import datetime
import cloudinary
import cloudinary.uploader
import pytz

# # Configure Cloudinary
# cloudinary.config(
#     cloud_name="your-cloud-name", api_key="your-api-key", api_secret="your-api-secret"
# )

EAT = pytz.timezone("Africa/Nairobi")


# Function to return the current time in EAT
def current_eat_time():
    return datetime.now(EAT)


class DocumentAPI(Resource):
    def get(self, id=None):
        if id is None:
            documents = Document.query.all()
            document_list = [document.to_dict() for document in documents]
            return make_response(jsonify(document_list), 200)
        else:
            document = Document.query.get(id)
            if not document:
                return make_response(jsonify({"msg": "Document not found"}), 404)
            return make_response(jsonify(document.to_dict()), 200)

    # Fetch all documents for a specific user (either parent or provider)

    def post(self):
        data = request.form  # Change to form if files are being uploaded
        file = request.files.get("file")

        if not data or not file:
            return make_response(
                jsonify({"msg": "No input data or file provided"}), 400
            )

        try:
            # Upload to Cloudinary (happyhearts folder)
            upload_result = cloudinary.uploader.upload(file, folder="happyhearts")

            # Create a new Document object
            new_document = Document(
                entityType=data.get("entityType"),
                documentType=upload_result["format"],
                fileName=upload_result["original_filename"],
                size=upload_result["bytes"],
                url=upload_result["secure_url"],
                parent_id=data.get("parent_id"),
                provider_id=data.get("provider_id"),
                timestamp=current_eat_time(),
            )

            # Save the document to the database
            db.session.add(new_document)
            db.session.commit()

            return make_response(
                jsonify(
                    {
                        "msg": "Document uploaded successfully",
                        "data": new_document.to_dict(),
                    }
                ),
                201,
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)
        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def put(self, id):
        document = Document.query.get(id)
        if not document:
            return make_response(jsonify({"msg": "Document not found"}), 404)

        data = request.json
        try:
            # Update document metadata
            for key, value in data.items():
                if hasattr(document, key):
                    setattr(document, key, value)

            db.session.commit()
            return make_response(
                jsonify(
                    {"msg": "Document updated successfully", "data": document.to_dict()}
                ),
                200,
            )

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return make_response(jsonify({"msg": f" {error_message}"}), 400)
        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)

    def delete(self, id):
        document = Document.query.get(id)
        if not document:
            return make_response(jsonify({"msg": "Document not found"}), 404)

        try:
            # Delete from Cloudinary
            cloudinary.uploader.destroy(document.url.split("/")[-1].split(".")[0])

            # Delete from database
            db.session.delete(document)
            db.session.commit()

            return make_response(jsonify({"msg": "Document deleted successfully"}), 200)

        except Exception as e:
            return make_response(jsonify({"msg": str(e)}), 500)


class DocumentByProvider(Resource):
    def get(self, id):
        # Fetch documents for the provider
        documents = Document.query.filter((Document.provider_id == id)).all()

        if not documents:
            return make_response(
                jsonify({"msg": "No documents found for this user"}), 404
            )

        document_list = [document.to_dict() for document in documents]
        return make_response(jsonify(document_list), 200)


class DocumentName(Resource):
    def get(self, filename):
        document = Document.query.filter_by(fileName=filename).first()
        if not document:
            return make_response(
                jsonify({"msg": "Document with that filename not found"}), 404
            )
        return make_response(jsonify(document.to_dict()), 200)


class DocumentByParent(Resource):
    def get(self, id):
        documents = Document.query.filter((Document.parent_id == id)).all()

        if not documents:
            return make_response(
                jsonify({"msg": "No documents found for this user"}), 404
            )

        document_list = [document.to_dict() for document in documents]
        return make_response(jsonify(document_list), 200)


class DocumentsByParentAndChild(Resource):
    def get(self, parent_id, child_id):
        documents = Document.query.filter(
            and_(Document.parent_id == parent_id, Document.child_id == child_id)
        ).all()
        return make_response(jsonify(documents.to_dict()), 200)


class DocumentByParentOnly(Resource):
    def get(
        self,
        parent_id,
    ):
        documents = (
            Document.query.filter(Document.parent_id == parent_id)
            .filter(Document.child_id is None)
            .all()
        )
        document_list = [document.to_dict() for document in documents]

        return make_response(jsonify(document_list), 200)
