import json


with open("config.json", "r") as f:
    json_config = json.load(f)


class Config:
    SECRET_KEY = json_config["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = json_config["DATABASE_URI"]
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = json_config["EMAIL_USER"]
    MAIL_PASSWORD = json_config["EMAIL_PASS"]