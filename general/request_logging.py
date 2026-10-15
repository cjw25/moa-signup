import logging
import os
import json
from datetime import datetime, timezone

import requests
from flask import g, request

log = logging.getLogger(__name__)


def register_request_logging(app):
    @app.after_request
    def record_request(response):
        if request.path == "/health":
            return response
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.path,
            "status": 200 if getattr(g, "event_type", None) == "login_success" else response.status_code,
            "event_type": getattr(g, "event_type", "http_request"),
        }
        print(json.dumps(event, ensure_ascii=False), flush=True)
        monitor_url = os.getenv("MONITOR_URL")
        token = os.getenv("EVENT_TOKEN")
        if monitor_url and token:
            try:
                result = requests.post(monitor_url, json=event, headers={"X-Event-Token": token}, timeout=2)
                result.raise_for_status()
            except requests.RequestException as exc:
                log.warning("감시 서버 전송 실패: %s", exc)
        elif monitor_url:
            log.warning("EVENT_TOKEN이 없어 감시 서버 전송을 건너뜁니다.")
        return response
