from flask import Blueprint, jsonify, request

from repositories import notes as repo
from routes.auth import login_required

notes = Blueprint("notes", __name__)
STATUSES = {"확인 전", "확인 중", "완료"}


def valid_input():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, None, None
    title, body, status = payload.get("title"), payload.get("body"), payload.get("status", "확인 전")
    if not isinstance(title, str) or not isinstance(body, str):
        return None, None, None
    return title.strip(), body.strip(), status if isinstance(status, str) else None


def invalid_input():
    return jsonify(message="제목과 내용 및 처리 상태를 확인해 주세요."), 400


def missing_note():
    return jsonify(message="메모를 찾을 수 없습니다."), 404


@notes.get("/api/notes")
@login_required
def list_notes():
    return jsonify(repo.list_notes())


@notes.get("/api/notes/<int:note_id>")
@login_required
def detail(note_id):
    note = repo.find_note(note_id)
    return jsonify(note) if note is not None else missing_note()


@notes.post("/api/notes")
@login_required
def create():
    title, body, status = valid_input()
    if not title or not body or status not in STATUSES:
        return invalid_input()
    return jsonify(repo.create_note(title, body, status)), 201


@notes.put("/api/notes/<int:note_id>")
@login_required
def update(note_id):
    if repo.find_note(note_id) is None:
        return missing_note()
    title, body, status = valid_input()
    if not title or not body or status not in STATUSES:
        return invalid_input()
    note = repo.update_note(note_id, title, body, status)
    return jsonify(note) if note is not None else missing_note()


@notes.delete("/api/notes/<int:note_id>")
@login_required
def delete(note_id):
    if repo.delete_note(note_id) is None:
        return missing_note()
    return "", 204
