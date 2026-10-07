import logging
import os
from datetime import datetime, timezone

import requests
from flask import request

log = logging.getLogger(__name__)


def register_request_logging(app):
    @app.after_request
    def record_request(response):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
        }
        log.info("request %s", event)
        monitor_url = os.getenv("MONITOR_URL")
        if monitor_url:
            try:
                requests.post(monitor_url, json=event, timeout=0.5)
            except requests.RequestException as exc:
                log.warning("감시 서버 전송 실패: %s", exc)
        return response
