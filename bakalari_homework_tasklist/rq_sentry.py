import os

dsn = os.environ.get("SENTRY_DSN", None)
if dsn is not None:
    import sentry_sdk
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.rq import RqIntegration

    sentry_sdk.init(dsn=dsn, integrations=[RqIntegration(), RedisIntegration()])
elif (
    os.environ.get("FLASK_ENV", "") != "development" and "FLASK_DEBUG" not in os.environ
):
    import warnings

    warnings.warn(Warning("Sentry is not active"))

# TODO: Once I manage to start catching errors from the task themselfves, add this:
# def add_user_info(event, hint):
#     try:
#         if "user_id" in event["task_args"]:
#             user_id = event["task_args"]["user_id"]
#             u = User.query.get(user_id)
#
#             user_info = event.setdefault("user", {})
#             user_info["id"] = user_id
#             user_info["url"] = u.url
#             user_info["username"] = u.username
#     except Exception:
#         pass
#     return event
