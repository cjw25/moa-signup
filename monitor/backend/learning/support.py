from datetime import datetime, timezone

from repositories import events as event_repo
from learning.normalize import normalize_events


def current_boundary():
    return event_repo.max_event_id()


def read_observation(after_id, reference_time):
    return normalize_events(event_repo.list_since(after_id, reference_time))


def first_reference_time():
    return datetime.now(timezone.utc)
