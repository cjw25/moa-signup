import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from routes.auth import auth
from request_logging import register_request_logging
from routes.posts import board
from observability import init_observability
from routes.auth import login_required


def create_app():
    load_dotenv()
    app = Flask(__name__)
    secret = os.getenv("SECRET_KEY") or os.getenv("GENERAL_SECRET_KEY")
    if not secret or secret == "REPLACE_WITH_A_LONG_RANDOM_HEX_VALUE":
        raise RuntimeError("SECRET_KEY를 .env에 설정해 주세요.")
    app.secret_key = secret
    app.config.update(SESSION_COOKIE_NAME="general_session", SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true")
    init_observability("mini-general")
    app.register_blueprint(auth)
    app.register_blueprint(board)

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/sentry-test")
    @login_required
    def sentry_test():
        if os.getenv("ENABLE_SENTRY_TEST", "false").lower() != "true":
            return jsonify(message="실습 경로가 꺼져 있습니다."), 404
        return jsonify(result=1 / 0)
    register_request_logging(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5100, debug=True)
