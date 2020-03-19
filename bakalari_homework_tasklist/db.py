from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    username = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, primary_key=True)
    token = db.Column(db.String)
    token_date = db.Column(db.Date)
    name = db.Column(db.String, nullable=False)
    account_type = db.Column(db.String, nullable=False)

    def get_id(self):
        return self.username, self.url


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_error = db.Column(db.Boolean, nullable=False)
    email = db.Column(db.String)
    text = db.Column(db.String, nullable=False)
