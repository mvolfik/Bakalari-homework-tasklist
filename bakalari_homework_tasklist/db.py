from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import List

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from jinja2.filters import do_truncate
from sqlalchemy import ForeignKey, UniqueConstraint

db = SQLAlchemy()

html_re = re.compile(r"<.+?>")


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


@dataclass(init=False, eq=False)
class Homework(db.Model):
    summary: str
    id: int = db.Column(db.Integer, primary_key=True)  # just for this app
    baka_id = db.Column(db.String, nullable=False)
    # baka_id is from the Bakaláři system, it can't be unique because:
    #            a) I have no idea if it is unique across schools (= Bakaláři instances)
    # but mainly b) Two users from same class will have the same homework (actually,
    #               I don't know if they have same IDs in the system...), but we want to
    #               keep their status separately
    # however, we store it to know if we already have this homework in this user's list
    # of homework

    assigned: datetime = db.Column(db.DateTime, nullable=False)
    due: datetime = db.Column(db.DateTime, nullable=False)
    subject: str = db.Column(db.String, nullable=False)
    subject_short: str = db.Column(db.String, nullable=False)
    description: str = db.Column(db.String)

    user_id = db.Column(db.Integer, ForeignKey(User.id), nullable=False)
    user = db.relationship(User, backref="homeworks")

    is_done: bool = db.Column(db.Boolean, nullable=False, default=False)
    postponed_until: date = db.Column(db.Date)

    attachments: List[Attachment] = db.relationship(
        "Attachment", back_populates="homework"
    )

    @property
    def summary(self) -> str:
        if self.description is None:
            return ""
        else:
            return do_truncate(
                None, html_re.sub("", self.description), 80, False, "&hellip;", 5
            )


@dataclass(init=False, eq=False)
class Attachment(db.Model):
    url: str
    id = db.Column(db.Integer, primary_key=True)
    # see note for Homework, though we don't need baka_id here, we just use it to create
    # the url when storing it

    filename: str = db.Column(db.String, nullable=False)
    url_placeholder = db.Column(db.String, nullable=False)
    # "{}" instead of token to be formatted with actual token later

    homework_id = db.Column(db.Integer, ForeignKey(Homework.id), nullable=False)
    homework = db.relationship(Homework, back_populates="attachments")

    @property
    def url(self) -> str:
        return self.url_placeholder.format(self.homework.user.token)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_error = db.Column(db.Boolean, nullable=False)
    email = db.Column(db.String)
    text = db.Column(db.String, nullable=False)
