import hmac
import os

from flask import Blueprint, jsonify, request

from repositories import events as repo
from event_rules import make_event
from routes.auth import login_required

events = Blueprint("events", __name__)


@events.get("/api/events")
@login_required
def list_events():
    path = request.args.get("path", "").strip()
    status_text = request.args.get("status", "").strip()
    if status_text:
        if not status_text.isdecimal() or not 100 <= int(status_text) <= 599:
            return jsonify(message="상태 코드는 100~599 사이 숫자여야 합니다."), 400
        status = int(status_text)
    else:
        status = None
    return jsonify(repo.list_events(path, status))


@events.post("/events")
@events.post("/api/events")
def receive_event():
    token = os.getenv("EVENT_TOKEN")
    if not token or not hmac.compare_digest(request.headers.get("X-Event-Token", ""), token):
        return jsonify(message="기록 전송 토큰이 올바르지 않습니다."), 403
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(message="JSON 요청이 필요합니다."), 400
    method, path, status = payload.get("method"), payload.get("path"), payload.get("status")
    event_type = payload.get("event_type", "http_request")
    if not isinstance(method, str) or not method or not isinstance(path, str) or not path or type(status) is not int or not 100 <= status <= 599:
        return jsonify(message="요청 기록 형식이 올바르지 않습니다."), 400
    if not isinstance(event_type, str) or event_type not in {"http_request", "login_failure", "login_success", "post_list", "request_error"}:
        return jsonify(message="기록 종류가 올바르지 않습니다."), 400
    repo.create_event(method, path, status, make_event(method, path, status, event_type))
    return "", 204
