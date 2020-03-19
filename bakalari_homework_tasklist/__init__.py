import locale
import os

from flask import Flask, before_render_template, render_template


def create_app(config=None, *, keep_default=True, **kwargs):
    locale.setlocale(locale.LC_ALL, "cs_CZ.utf8")
    app = Flask(__name__)

    # --- template helpers
    from .utils import create_navbar, get_grouped_flashes

    app.add_template_global(get_grouped_flashes)
    before_render_template.connect(create_navbar, app)

    # --- config
    app.config.from_mapping(SQLALCHEMY_TRACK_MODIFICATIONS=False)
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

    from .auth import bp, login_manager

    app.register_blueprint(bp)
    login_manager.init_app(app)

    from .core import bp

    app.register_blueprint(bp)

    # --- home route
    @app.route("/")
    def home():
        return render_template("home.html")

    # --- 500 error handler
    @app.errorhandler(500)
    def error500(_):
        return render_template("error500.html", active_endpoint=""), 500

    @app.errorhandler(404)
    def error404(_):
        return render_template("error404.html", active_endpoint=""), 404

    from . import sentry  # just import, it does everything by itself

    return app
