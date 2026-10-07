from flask import Blueprint, jsonify, request

from repositories import notes as repo

notes = Blueprint("notes", __name__)


def valid_input():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, None
    title, body = payload.get("title"), payload.get("body")
    if not isinstance(title, str) or not isinstance(body, str):
        return None, None
    return title.strip(), body.strip()


def invalid_input():
    return jsonify(message="제목과 내용을 모두 입력해 주세요."), 400


def missing_note():
    return jsonify(message="메모를 찾을 수 없습니다."), 404


@notes.get("/api/notes")
def list_notes():
    return jsonify(repo.list_notes())


@notes.get("/api/notes/<int:note_id>")
def detail(note_id):
    note = repo.find_note(note_id)
    return jsonify(note) if note is not None else missing_note()


@notes.post("/api/notes")
def create():
    title, body = valid_input()
    if not title or not body:
        return invalid_input()
    return jsonify(repo.create_note(title, body)), 201


@notes.put("/api/notes/<int:note_id>")
def update(note_id):
    if repo.find_note(note_id) is None:
        return missing_note()
    title, body = valid_input()
    if not title or not body:
        return invalid_input()
    note = repo.update_note(note_id, title, body)
    return jsonify(note) if note is not None else missing_note()


@notes.delete("/api/notes/<int:note_id>")
def delete(note_id):
    if repo.delete_note(note_id) is None:
        return missing_note()
    return "", 204
