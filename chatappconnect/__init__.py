import os
import json
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_mail import Mail


app = Flask(__name__)

with open("config.json", "r") as f:
    app.json_variables = json.load(f)

app.config["SECRET_KEY"] = "0f0a2448bd028146bfa8f615ff308525"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = app.json_variables["EMAIL_USER"]
app.config["MAIL_PASSWORD"] = app.json_variables["EMAIL_PASS"]
# app.add_url_rule('/favicon.ico',
#                  redirect_to=url_for('static', filename='favicon.ico'))

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
mail = Mail(app)

from chatappconnect import routes
