import os

dsn = os.environ.get("SENTRY_DSN", None)
if dsn is not None:
    import sentry_sdk
    from flask import request
    from flask_login import current_user
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.rq import RqIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

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
        dsn=dsn,
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration(),
            RqIntegration(),
            RedisIntegration(),
        ],
        before_send=add_user_info,
    )
elif (
    os.environ.get("FLASK_ENV", "") != "development" and "FLASK_DEBUG" not in os.environ
):

    import warnings

    warnings.warn(Warning("Sentry is not active"))
