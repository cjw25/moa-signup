import json
import sys

from learning.http_rules import assess
from learning.lesson2 import load_observation
from learning.normalize import normalize_events


def main():
    threshold = int(sys.argv[1]) if len(sys.argv) == 2 else 10
    result = assess(normalize_events(load_observation()["records"]), threshold)
    print(json.dumps({"count": result["count"], "threshold": threshold,
                      "candidate": result["candidate"], "view_ids": result["view_ids"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
