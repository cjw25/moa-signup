import logging
import os
from datetime import datetime, timezone

import requests
from flask import g, request

log = logging.getLogger(__name__)


def register_request_logging(app):
    @app.after_request
    def record_request(response):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.path,
            "status": 200 if getattr(g, "event_type", None) == "login_success" else response.status_code,
            "event_type": getattr(g, "event_type", "http_request"),
        }
        log.info("request %s", event)
        monitor_url = os.getenv("MONITOR_URL")
        if monitor_url:
            try:
                requests.post(monitor_url, json=event, timeout=2)
            except requests.RequestException as exc:
                log.warning("감시 서버 전송 실패: %s", exc)
        return response
