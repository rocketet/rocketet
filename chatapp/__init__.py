from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config["SECRET_KEY"] = "0f0a2448bd028146bfa8f615ff308525"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy(app)

from chatapp import routes