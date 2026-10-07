from flask import Blueprint, redirect, render_template, request, url_for

from post_rules import validate_post
from repositories import posts

board = Blueprint("board", __name__)


def missing_post():
    return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404


@board.get("/")
def index():
    return render_template("index.html", posts=posts.list_posts())


@board.get("/board/<int:post_id>")
def detail(post_id):
    post = posts.find_post(post_id)
    if post is None:
        return missing_post()
    return render_template("detail.html", post=post)


@board.route("/board/new", methods=["GET", "POST"])
def new():
    if request.method == "GET":
        return render_template("new.html", title="", body="")
    title, body, error = validate_post(request.form.get("title"), request.form.get("body"))
    if error:
        return render_template("new.html", title=title, body=body, error=error), 400
    post = posts.create_post(title, body)
    return redirect(url_for("board.detail", post_id=post[0]), code=303)


@board.route("/board/<int:post_id>/edit", methods=["GET", "POST"])
def edit(post_id):
    post = posts.find_post(post_id)
    if post is None:
        return missing_post()
    if request.method == "GET":
        return render_template("edit.html", post=post, title=post[1], body=post[2])
    title, body, error = validate_post(request.form.get("title"), request.form.get("body"))
    if error:
        return render_template("edit.html", post=post, title=title, body=body, error=error), 400
    if posts.update_post(post_id, title, body) is None:
        return missing_post()
    return redirect(url_for("board.detail", post_id=post_id), code=303)


@board.route("/board/<int:post_id>/delete", methods=["GET", "POST"])
def delete(post_id):
    if request.method == "GET":
        post = posts.find_post(post_id)
        if post is None:
            return missing_post()
        return render_template("delete.html", post=post)
    if posts.delete_post(post_id) is None:
        return missing_post()
    return redirect(url_for("board.index"), code=303)
