import os

os.environ.setdefault("GENERAL_SECRET_KEY", "unit-test-general-session-key")

from app import create_app
from repositories import posts
from routes import auth
from werkzeug.security import generate_password_hash


def test_board_flow(monkeypatch):
    monkeypatch.setenv("GENERAL_SECRET_KEY", "unit-test-general-session-key")
    data = {}
    next_id = iter(range(1, 100))

    monkeypatch.delenv("MONITOR_URL", raising=False)
    monkeypatch.setattr(posts, "list_posts", lambda: [(key, value[0]) for key, value in sorted(data.items())])
    monkeypatch.setattr(posts, "find_post", lambda post_id: (post_id, *data[post_id]) if post_id in data else None)

    def create(title, body):
        post_id = next(next_id)
        data[post_id] = (title, body)
        return (post_id,)

    def update(post_id, title, body):
        if post_id not in data:
            return None
        data[post_id] = (title, body)
        return (post_id,)

    def delete(post_id):
        if post_id not in data:
            return None
        del data[post_id]
        return (post_id,)

    monkeypatch.setattr(posts, "create_post", create)
    monkeypatch.setattr(posts, "update_post", update)
    monkeypatch.setattr(posts, "delete_post", delete)
    client = create_app().test_client()

    assert client.get("/").status_code == 302
    with client.session_transaction() as session:
        session["user"] = {"id": 1, "username": "student"}

    assert "등록된 게시글이 없습니다." in client.get("/").get_data(as_text=True)
    assert client.post("/board/new", data={"title": " ", "body": "본문"}).status_code == 400
    assert data == {}

    response = client.post("/board/new", data={"title": " 제목 ", "body": " 본문 "})
    assert response.status_code == 303
    assert response.headers["Location"].endswith("/board/1")
    assert data[1] == ("제목", "본문")
    assert client.get("/board/1").status_code == 200
    assert len(data) == 1

    assert client.get("/board/1/edit").status_code == 200
    assert client.post("/board/1/edit", data={"title": "", "body": "변경"}).status_code == 400
    assert data[1] == ("제목", "본문")
    assert client.post("/board/1/edit", data={"title": "수정", "body": "변경"}).status_code == 303
    assert data[1] == ("수정", "변경")

    assert client.get("/board/1/delete").status_code == 200
    assert 1 in data
    assert client.post("/board/1/delete").status_code == 303
    assert client.get("/board/1").status_code == 404
    assert client.get("/board/1/edit").status_code == 404
    assert client.get("/board/1/delete").status_code == 404


def test_login_sends_typed_events(monkeypatch):
    monkeypatch.setenv("GENERAL_SECRET_KEY", "unit-test-general-session-key")
    sent = []
    monkeypatch.setenv("MONITOR_URL", "http://monitor-api:5000/api/events")
    monkeypatch.setenv("EVENT_TOKEN", "test-event-token")
    monkeypatch.setattr(auth, "find_user", lambda username: {
        "id": 1, "username": "student", "password_hash": generate_password_hash("Learn123!")
    } if username == "student" else None)
    monkeypatch.setattr("request_logging.requests.post", lambda url, json, headers, timeout: (sent.append((url, json, headers)) or type("Response", (), {"raise_for_status": lambda self: None})()))
    monkeypatch.setattr(posts, "list_posts", lambda: [])
    client = create_app().test_client()

    assert client.post("/login", data={"username": "student", "password": "wrong"}).status_code == 401
    assert sent[-1][1]["event_type"] == "login_failure"
    assert sent[-1][1]["status"] == 401
    assert client.post("/login", data={"username": "student", "password": "Learn123!"}).status_code == 303
    assert sent[-1][1]["event_type"] == "login_success"
    assert sent[-1][1]["status"] == 200
    assert sent[-1][2]["X-Event-Token"] == "test-event-token"
    assert client.get("/").status_code == 200
    assert client.post("/logout").status_code == 303
    assert client.get("/").status_code == 302
