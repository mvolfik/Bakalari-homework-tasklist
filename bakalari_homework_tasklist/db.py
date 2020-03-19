from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, UniqueConstraint

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # just for this app
    username = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    token = db.Column(db.String)
    token_date = db.Column(db.Date)
    name = db.Column(db.String, nullable=False)
    account_type = db.Column(db.String, nullable=False)

    __table_args__ = (
        UniqueConstraint(username, url),
        # this combination should be unique, we don't use it as a primary key just to
        # prevent complex foreign keys
    )


class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # just for this app
    baka_id = db.Column(db.String, nullable=False)
    # baka_id is from the Bakaláři system, it can't be unique because:
    #            a) I have no idea if it is unique across schools (= Bakaláři instances)
    # but mainly b) Two users from same class will have the same homework (actually,
    #               I don't know if they have same IDs in the system...), but we want to
    #               keep their status separately

    assigned = db.Column(db.DateTime, nullable=False)
    due = db.Column(db.DateTime, nullable=False)
    subject = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    user_id = db.Column(db.Integer, ForeignKey(User.id), nullable=False)
    user = db.relationship(User, backref="homeworks")


class Attachment(db.Model):
    id = db.Column(db.String, primary_key=True)
    # see note for Homework, though we don't need baka_id here, we just use it when
    # storing to create dl_link

    filename = db.Column(db.String, nullable=False)
    dl_link = db.Column(db.String, nullable=False)
    # "{}" instead of token to be formatted with actual token later

    homework_id = db.Column(db.Integer, ForeignKey(Homework.id), nullable=False)
    homework = db.relationship(Homework, backref="attachments")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_error = db.Column(db.Boolean, nullable=False)
    email = db.Column(db.String)
    text = db.Column(db.String, nullable=False)
