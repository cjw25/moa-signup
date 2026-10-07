"""Run against the three services' shared PostgreSQL database in CI."""

import os
import time

import psycopg
import requests
from werkzeug.security import generate_password_hash


BOARD = "http://127.0.0.1:5100"
MONITOR = "http://127.0.0.1:5200"
FRONTEND = "http://127.0.0.1:5173"
API = FRONTEND + "/api"


def ready(url):
    for _ in range(50):
        try:
            if requests.get(url, timeout=1).status_code < 500:
                return
        except requests.RequestException:
            pass
        time.sleep(0.2)
    raise AssertionError(f"Service did not start: {url}")


def check(response, status):
    assert response.status_code == status, (response.status_code, response.text)
    return response


def main():
    ready(BOARD)
    ready(MONITOR + "/api/events")
    ready(FRONTEND)
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute(
            "INSERT INTO monitor_users (username, display_name, password_hash) "
            "VALUES (%s, %s, %s)",
            ("ci-admin", "CI 운영자", generate_password_hash("correct-password")),
        )

    check(requests.get(API + "/events"), 401)
    check(requests.get(API + "/notes"), 401)
    check(requests.post(API + "/auth/login", json={"username": "", "password": "x"}), 400)
    check(requests.post(API + "/auth/login", json={"username": "ci-admin", "password": "wrong"}), 401)
    browser = requests.Session()
    user = check(browser.post(API + "/auth/login", json={"username": "ci-admin", "password": "correct-password"}), 200).json()
    assert user["user"]["name"] == "CI 운영자"
    assert check(browser.get(API + "/auth/me"), 200).json()["user"]["name"] == "CI 운영자"
    assert isinstance(check(browser.get(API + "/events"), 200).json(), list)

    check(requests.post(BOARD + "/board/new", data={"title": " ", "body": "본문"}), 400)
    created = check(requests.post(BOARD + "/board/new", data={"title": " 제목 ", "body": " 본문 "}, allow_redirects=False), 303)
    detail_path = created.headers["Location"]
    check(requests.get(BOARD + detail_path), 200)
    check(requests.get(BOARD + "/board/999999"), 404)
    post_id = int(detail_path.rsplit("/", 1)[-1])
    check(requests.post(BOARD + f"/board/{post_id}/edit", data={"title": "", "body": "변경"}), 400)
    check(requests.post(BOARD + f"/board/{post_id}/edit", data={"title": "수정", "body": "변경"}, allow_redirects=False), 303)
    assert "수정" in check(requests.get(BOARD + detail_path), 200).text
    check(requests.get(BOARD + f"/board/{post_id}/delete"), 200)
    check(requests.post(BOARD + f"/board/{post_id}/delete", allow_redirects=False), 303)
    check(requests.get(BOARD + detail_path), 404)

    events = check(browser.get(API + "/events"), 200).json()
    assert any(e["path"] == "/board/999999" and e["status_code"] == 404 for e in events)
    assert any(e["path"] == detail_path and e["method"] == "GET" for e in events)
    filtered = check(browser.get(API + "/events", params={"path": "/board/999999", "status": 404}), 200).json()
    assert len(filtered) >= 1 and all(e["status_code"] == 404 and "/board/999999" in e["path"] for e in filtered)
    assert len(check(browser.get(API + "/events"), 200).json()) >= len(filtered)
    check(browser.get(API + "/events", params={"status": "bad"}), 400)
    check(browser.post(API + "/notes", json={"title": " ", "body": "내용"}), 400)
    note = check(browser.post(API + "/notes", json={"title": " 제목 ", "body": " 내용 "}), 201).json()
    note_id = note["id"]
    assert note["title"] == "제목"
    assert note["status"] == "확인 전"
    assert check(browser.get(API + f"/notes/{note_id}"), 200).json()["body"] == "내용"
    check(browser.put(API + f"/notes/{note_id}", json={"title": "수정", "body": " "}), 400)
    assert check(browser.get(API + f"/notes/{note_id}"), 200).json()["body"] == "내용"
    check(browser.put(API + f"/notes/{note_id}", json={"title": "수정", "body": "변경", "status": "완료"}), 200)
    assert any(n["id"] == note_id and n["body"] == "변경" and n["status"] == "완료" for n in check(browser.get(API + "/notes"), 200).json())
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        assert conn.execute("SELECT body, status FROM observation_notes WHERE id = %s", (note_id,)).fetchone() == ("변경", "완료")
        assert conn.execute("SELECT COUNT(*) FROM request_events").fetchone()[0] > 0
    check(browser.delete(API + f"/notes/{note_id}"), 204)
    check(browser.get(API + f"/notes/{note_id}"), 404)
    check(browser.put(API + f"/notes/{note_id}", json={"title": "x", "body": "y"}), 404)
    check(browser.delete(API + f"/notes/{note_id}"), 404)
    check(browser.post(API + "/auth/logout"), 204)
    check(browser.get(API + "/auth/me"), 401)
    check(browser.get(API + "/notes"), 401)
    print("PostgreSQL integration scenario passed")


if __name__ == "__main__":
    main()
