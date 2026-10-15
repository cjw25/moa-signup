from datetime import datetime, timedelta, timezone

from event_rules import make_event
from learning.http_rules import assess, find_following_errors, select_views
from learning.normalize import normalize_event
from learning.report import build_report


def row(number, seconds, method="GET", path="/", status=200, kind="post_list"):
    return {"id": number, "occurred_at": (datetime(2026, 10, 15, tzinfo=timezone.utc)
            + timedelta(seconds=seconds)).isoformat(), "method": method, "path": path,
            "status_code": status, "event_type": kind}


def test_classification_and_normalization_preserve_origin():
    assert make_event("GET", "/", 200) == "post_list"
    assert make_event("GET", "/training-missing", 404) == "request_error"
    assert make_event("POST", "/login", 401, "login_failure") == "login_failure"
    original = row(7, 1)
    normalized = normalize_event(original)
    assert original["id"] == 7
    assert normalized["id"] == "http-7"
    assert normalized["source"] == "http_live" and normalized["kind"] == "post_list"
    assert normalized["occurred_at"] == original["occurred_at"]
    assert "user" not in normalized and "ip" not in normalized


def test_view_conditions_threshold_and_following_window():
    rows = [normalize_event(row(1, 0)), normalize_event(row(2, 1, method="POST")),
            normalize_event(row(3, 2, path="/other")), normalize_event(row(4, 3, status=201)),
            normalize_event(row(5, 4, kind="http_request")),
            normalize_event(row(6, 5, path="/training-missing", status=404, kind="request_error")),
            normalize_event(row(7, 30, path="/training-missing", status=404, kind="request_error")),
            normalize_event(row(8, 31, path="/training-missing", status=404, kind="request_error"))]
    views = select_views(rows)
    assert [event["id"] for event in views] == ["http-1"]
    assert [event["id"] for event in find_following_errors(rows, views)] == ["http-6", "http-7"]
    assert find_following_errors(rows, []) == []
    assert assess(rows, 1)["candidate"] is True
    assert assess(rows, 2)["candidate"] is False
    report = build_report(rows, 1, 0, datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert report["observed_count"] == 1 and len(report["evidence"]) == 3


def test_twelve_views_are_counted_without_the_following_404():
    rows = [normalize_event(row(number, number)) for number in range(1, 13)]
    rows.append(normalize_event(row(13, 13, path="/training-missing", status=404, kind="request_error")))
    first = assess(rows, 10)
    second = assess(rows, 20)
    assert first["count"] == second["count"] == 12
    assert first["candidate"] is True and second["candidate"] is False
    assert len(first["view_ids"]) == 12 and len(first["following_errors"]) == 1
