from werkzeug.security import generate_password_hash

from app import create_app
from routes import auth, events, notes


def test_login_and_validation(monkeypatch):
    monkeypatch.setattr(auth, "find_user", lambda username: {
        "id": 1, "username": username, "display_name": "운영자",
        "password_hash": generate_password_hash("correct-password"),
    } if username == "admin" else None)
    client = create_app().test_client()
    assert client.post("/api/auth/login", json={"username": "", "password": "x"}).status_code == 400
    assert client.post("/api/auth/login", json={"username": "admin", "password": "wrong"}).status_code == 401
    response = client.post("/api/auth/login", json={"username": "admin", "password": "correct-password"})
    assert response.status_code == 200
    assert response.json["user"]["name"] == "운영자"


def test_event_and_note_routes(monkeypatch):
    stored_events = []
    stored_notes = {}
    next_id = iter(range(1, 100))
    monkeypatch.setattr(events.repo, "list_events", lambda: stored_events)
    monkeypatch.setattr(events.repo, "create_event", lambda method, path, status, at: stored_events.append({"id": 1, "method": method, "path": path, "status_code": status, "occurred_at": at.isoformat()}))
    monkeypatch.setattr(notes.repo, "list_notes", lambda: list(stored_notes.values()))
    monkeypatch.setattr(notes.repo, "find_note", lambda id: stored_notes.get(id))

    def create(title, body):
        id = next(next_id)
        stored_notes[id] = {"id": id, "title": title, "body": body}
        return stored_notes[id]

    def update(id, title, body):
        if id not in stored_notes:
            return None
        stored_notes[id] = {"id": id, "title": title, "body": body}
        return stored_notes[id]

    def delete(id):
        return stored_notes.pop(id, None)

    monkeypatch.setattr(notes.repo, "create_note", create)
    monkeypatch.setattr(notes.repo, "update_note", update)
    monkeypatch.setattr(notes.repo, "delete_note", delete)
    client = create_app().test_client()

    assert client.post("/events", json={"method": "GET", "path": "/board/999", "status": 404, "timestamp": "2026-10-07T00:00:00+00:00"}).status_code == 204
    assert client.get("/api/events").json[0]["status_code"] == 404
    assert client.post("/api/notes", json={"title": " ", "body": "내용"}).status_code == 400
    assert client.get("/api/notes").json == []
    created = client.post("/api/notes", json={"title": " 제목 ", "body": " 내용 "})
    assert created.status_code == 201
    assert created.json["title"] == "제목"
    assert client.get("/api/notes/1").json["body"] == "내용"
    assert client.put("/api/notes/1", json={"title": "수정", "body": " "}).status_code == 400
    assert stored_notes[1]["body"] == "내용"
    assert client.put("/api/notes/1", json={"title": "수정", "body": "변경"}).status_code == 200
    assert client.delete("/api/notes/1").status_code == 204
    assert client.get("/api/notes/1").status_code == 404
    assert client.put("/api/notes/1", json={"title": "x", "body": "y"}).status_code == 404
    assert client.delete("/api/notes/1").status_code == 404
