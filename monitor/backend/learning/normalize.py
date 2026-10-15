from datetime import datetime


def normalize_event(original):
    event = dict(original)
    raw_id = event["id"]
    if isinstance(raw_id, bool) or not isinstance(raw_id, int):
        raise ValueError("원본 ID는 숫자여야 합니다.")
    event["id"] = f"http-{raw_id}"
    event["source"] = "http_live"
    event["kind"] = original["event_type"]
    if isinstance(event["occurred_at"], datetime):
        event["occurred_at"] = event["occurred_at"].isoformat()
    return event


def normalize_events(rows):
    return [normalize_event(row) for row in rows]
