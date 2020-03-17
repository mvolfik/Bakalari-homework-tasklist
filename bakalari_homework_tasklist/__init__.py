import locale
import os
from collections import defaultdict

from flask import Flask, get_flashed_messages, render_template


def create_app(config=None, *, keep_default=True, **kwargs):
    locale.setlocale(locale.LC_ALL, "cs_CZ.utf8")
    app = Flask(__name__)

    @app.template_global()
    def get_grouped_flashes():
        """Returns a dictionary with group names as keys and lists of messages as values"""
        msgs = get_flashed_messages(with_categories=True)
        groups = defaultdict(list)
        for group, msg in msgs:
            groups[group].append(msg)
        return groups

    # --- config
    app.config.from_mapping(
        FLASH_COLORS={
            "ERROR_RED": "#F99",
            "CONFIRMATION_GREEN": "#4BB543",
            "INFO_YELLOW": "#FCF712",
            "WARNING_ORANGE": "#FF6700",
        },
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if keep_default:
        app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI=os.environ["DATABASE_URL"],
            SQLALCHEMY_ECHO=True,
            SECRET_KEY=os.environ["SECRET_KEY"],
        )
    if config is not None:
        app.config.from_mapping(config)
    if kwargs:
        app.config.from_mapping(kwargs)

    # --- blueprints and plugins registration
    from .db import db

    db.init_app(app)

    # --- homepage
    navigation_bar = (("home", "Úvodní stránka", None),)
    app.add_template_global(navigation_bar, "navigation_bar")

    @app.route("/")
    def home():
        return render_template("home.html")

    return app
