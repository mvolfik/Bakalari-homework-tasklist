import os

import sentry_sdk
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"], integrations=[RqIntegration(), RedisIntegration()]
)

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
