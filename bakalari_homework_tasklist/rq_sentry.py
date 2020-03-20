import os

import sentry_sdk
from sentry_sdk.integrations.rq import RqIntegration

sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], integrations=[RqIntegration()])
