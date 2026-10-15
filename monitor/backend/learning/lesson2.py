import json
from pathlib import Path

from learning.normalize import normalize_events

DATA = Path(__file__).parent / "data" / "observation.json"


def load_observation():
    with DATA.open(encoding="utf-8") as source:
        return json.load(source)


def main():
    rows = normalize_events(load_observation()["records"])
    print(json.dumps({"normalized_count": len(rows), "ids": [row["id"] for row in rows]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
