"""Documentation-only addresses, unrelated to the board's HTTP records."""
import json


def matches_ioc(value, indicators):
    return value in indicators


def main():
    indicators = {"203.0.113.10"}
    print(json.dumps({"source": "문서용 IP 예제", "matching": matches_ioc("203.0.113.10", indicators),
                      "nonmatching": matches_ioc("198.51.100.7", indicators)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
