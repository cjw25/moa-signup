import json

from learning.http_rules import select_views
from learning.lesson2 import load_observation
from learning.normalize import normalize_events


def main():
    views = select_views(normalize_events(load_observation()["records"]))
    print(json.dumps({"view_count": len(views), "view_ids": [view["id"] for view in views]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
