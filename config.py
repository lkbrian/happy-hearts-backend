import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = ("a0f7c9f0aaf84d96c1aeed05b3de2fb9d1e717c8577b7e7e635d25b7d1842c1d")
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.json.compact = False

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)
db.init_app(app)

jwt = JWTManager()
jwt.init_app(app)

api = Api(app)
migrate = Migrate(app, db)
CORS(app)

mail = Mail(app)
scheduler = BackgroundScheduler()

# constants.py

valid_roles = [
    "admin",
    "reception_desk",
    "accounts_desk",
]
