from datetime import datetime


def select_views(events):
    return [event for event in events if event["method"] == "GET"
            and event["path"] == "/" and event["status_code"] == 200
            and event["kind"] == "post_list"]


def find_following_errors(events, views):
    if not views:
        return []
    last_view = max(datetime.fromisoformat(view["occurred_at"]) for view in views)
    return [event for event in events
            if event["status_code"] == 404
            and 0 < (datetime.fromisoformat(event["occurred_at"]) - last_view).total_seconds() <= 30]


def assess(events, threshold):
    views = select_views(events)
    errors = find_following_errors(events, views)
    count = len(views)
    return {
        "count": count,
        "threshold": threshold,
        "candidate": count >= threshold,
        "view_ids": [event["id"] for event in views],
        "views": views,
        "following_errors": errors,
    }
