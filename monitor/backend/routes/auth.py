from functools import wraps

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

from repositories.users import find_user

auth = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return jsonify(message="로그인이 필요합니다."), 401
        return view(*args, **kwargs)

    return wrapped


@auth.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(message="JSON 요청이 필요합니다."), 400
    username = payload.get("username")
    password = payload.get("password")
    if not isinstance(username, str) or not username.strip() or not isinstance(password, str) or not password.strip():
        return jsonify(message="아이디와 비밀번호를 입력해 주세요."), 400
    user = find_user(username.strip())
    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify(message="아이디 또는 비밀번호가 올바르지 않습니다."), 401
    public_user = {"id": user["id"], "username": user["username"], "name": user["display_name"]}
    session.clear()
    session["user"] = public_user
    return jsonify(user=public_user)


@auth.get("/api/auth/me")
@login_required
def me():
    return jsonify(user=session["user"])


@auth.post("/api/auth/logout")
def logout():
    session.clear()
    return "", 204
