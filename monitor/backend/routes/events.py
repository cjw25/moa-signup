from datetime import datetime

from flask import Blueprint, jsonify, request

from repositories import events as repo

events = Blueprint("events", __name__)


@events.get("/api/events")
def list_events():
    return jsonify(repo.list_events())


@events.post("/events")
def receive_event():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(message="JSON 요청이 필요합니다."), 400
    method, path, status = payload.get("method"), payload.get("path"), payload.get("status")
    if not isinstance(method, str) or not method or not isinstance(path, str) or not path or type(status) is not int or not 100 <= status <= 599:
        return jsonify(message="요청 기록 형식이 올바르지 않습니다."), 400
    try:
        occurred_at = datetime.fromisoformat(payload["timestamp"])
    except (KeyError, TypeError, ValueError):
        return jsonify(message="요청 시각이 올바르지 않습니다."), 400
    repo.create_event(method, path, status, occurred_at)
    return "", 204
