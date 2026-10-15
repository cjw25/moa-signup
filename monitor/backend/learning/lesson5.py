import json

from learning.http_rules import find_following_errors, select_views
from learning.lesson2 import load_observation
from learning.normalize import normalize_events


def main():
    rows = normalize_events(load_observation()["records"])
    errors = find_following_errors(rows, select_views(rows))
    print(json.dumps({"following_error_ids": [event["id"] for event in errors]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
