import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[FlaskIntegration(), SqlalchemyIntegration()],
)
