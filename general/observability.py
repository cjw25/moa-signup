import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def remove_private_data(event, hint):
    event.pop("user", None)
    request = event.get("request")
    if isinstance(request, dict):
        for key in ("data", "cookies", "headers", "env", "query_string"):
            request.pop(key, None)
    return event


def init_observability(service):
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()],
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        release=os.getenv("APP_VERSION"),
        send_default_pii=False,
        max_request_body_size="never",
        before_send=remove_private_data,
        traces_sample_rate=0.0,
    )
    sentry_sdk.set_tag("service", service)
