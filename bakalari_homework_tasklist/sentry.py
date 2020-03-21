import os

import sentry_sdk
from flask import request
from flask_login import current_user
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.rq import RqIntegration


def add_user_info(event, hint):
    try:
        user_info = event.setdefault("user", {})
        if current_user.is_authenticated:
            user_info["id"] = current_user.id
            user_info["url"] = current_user.url
            user_info["username"] = current_user.username
        else:
            user_info["ip_address"] = request.remote_addr
    except Exception:
        pass
    return event


sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[
        FlaskIntegration(),
        SqlalchemyIntegration(),
        RqIntegration(),
        RedisIntegration(),
    ],
    before_send=add_user_info,
)
