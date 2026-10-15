"""Make actual requests through the local general Flask service and export its DB rows."""
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

from repositories import events as event_repo


def capture_case(view_count):
    if not 1 <= view_count <= 100:
        raise ValueError("조회 횟수는 1~100 사이여야 합니다.")
    username = os.getenv("CAPTURE_USERNAME")
    password = os.getenv("CAPTURE_PASSWORD")
    if not username or not password:
        raise RuntimeError("로컬 Compose 환경에 CAPTURE_USERNAME과 CAPTURE_PASSWORD를 설정해 주세요.")
    base = os.getenv("GENERAL_CAPTURE_URL", "http://general-api:5000").rstrip("/")
    session = requests.Session()
    login = session.post(f"{base}/login", data={"username": username, "password": password},
                         allow_redirects=False, timeout=5)
    if login.status_code != 303:
        raise RuntimeError(f"일반 게시판 로그인 실패: HTTP {login.status_code}")
    after_id = event_repo.max_event_id()  # Login event is outside this exercise's rows.
    for _ in range(view_count):
        response = session.get(f"{base}/", timeout=5)
        if response.status_code != 200:
            raise RuntimeError(f"게시글 목록 요청 실패: HTTP {response.status_code}")
    missing = session.get(f"{base}/training-missing", timeout=5)
    if missing.status_code != 404:
        raise RuntimeError(f"없는 경로 요청 결과가 404가 아닙니다: HTTP {missing.status_code}")
    for _ in range(20):
        rows = event_repo.list_since(after_id)
        if len(rows) >= view_count + 1:
            break
        time.sleep(0.25)
    else:
        raise RuntimeError("감시 DB에 모든 요청이 저장되지 않았습니다. 일반 앱의 전송 경고를 확인하세요.")
    return {
        "after_id": after_id,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "records": [{**dict(row), "occurred_at": row["occurred_at"].isoformat()} for row in rows],
    }


def main():
    try:
        count = int(sys.argv[1]) if len(sys.argv) == 2 else 4
        result = capture_case(count)
    except (ValueError, RuntimeError, requests.RequestException) as exc:
        print(f"캡처 실패: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
