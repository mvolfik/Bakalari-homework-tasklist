import locale
import os

import rq
from flask import Flask, before_render_template, redirect, render_template, url_for
from flask_wtf import CSRFProtect
from redis import Redis


def create_app(config=None, *, keep_default=True, **kwargs):
    locale.setlocale(locale.LC_ALL, "cs_CZ.utf8")
    app = Flask(__name__)

    # --- template helpers
    from .utils import create_navbar, get_grouped_flashes, BetterJSONEncoder

    app.json_encoder = BetterJSONEncoder

    app.add_template_global(get_grouped_flashes)
    before_render_template.connect(create_navbar, app)

    # --- config
    app.config.from_mapping(SQLALCHEMY_TRACK_MODIFICATIONS=False)
    if keep_default:
        app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI=os.environ["DATABASE_URL"],
            REDIS_URL=os.environ["REDIS_URL"],
            SQLALCHEMY_ECHO=False,
            SECRET_KEY=os.environ["SECRET_KEY"],
            PAUSE_REQUESTS=True,
            SERVICE_MESSAGE=os.environ.get("SERVICE_MESSAGE", None),
        )
    if config is not None:
        app.config.from_mapping(config)
    if kwargs:
        app.config.from_mapping(kwargs)

    # --- blueprints and plugins registration
    CSRFProtect(app)
    from .db import db

    db.init_app(app)

    from .auth import bp, login_manager

    app.register_blueprint(bp)
    login_manager.init_app(app)

    from .core import bp

    app.register_blueprint(bp)
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.task_queue = rq.Queue("homework-fetcher", connection=app.redis)
    from .api import bp

    app.register_blueprint(bp)

    # --- home route
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/favicon.ico")
    def faviconred():
        return redirect(url_for("static", filename="favicon.ico"))

    # --- 500 error handler
    @app.errorhandler(500)
    def error500(_):
        return render_template("error500.html", active_endpoint=""), 500

    @app.errorhandler(404)
    def error404(_):
        return render_template("error404.html", active_endpoint=""), 404

    from . import sentry  # just import, it does everything by itself

    return app
