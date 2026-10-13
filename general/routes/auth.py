from functools import wraps

from flask import Blueprint, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from repositories.users import find_user

auth = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password.strip():
        g.event_type = "login_failure"
        return render_template("login.html", error="아이디와 비밀번호를 입력해 주세요.", username=username), 401
    user = find_user(username)
    if user is None or not check_password_hash(user["password_hash"], password):
        g.event_type = "login_failure"
        return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다.", username=username), 401
    session.clear()
    session["user"] = {"id": user["id"], "username": user["username"]}
    g.event_type = "login_success"
    return redirect(url_for("board.index"), code=303)


@auth.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"), code=303)
