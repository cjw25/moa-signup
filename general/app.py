import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from db import connect_db
from routes.auth import auth
from request_logging import register_request_logging
from routes.posts import board


def create_app():
    load_dotenv()
    app = Flask(__name__)
    secret = os.getenv("GENERAL_SECRET_KEY")
    if not secret or secret == "REPLACE_WITH_A_LONG_RANDOM_HEX_VALUE":
        raise RuntimeError("GENERAL_SECRET_KEY를 .env에 설정해 주세요.")
    app.secret_key = secret
    app.config.update(SESSION_COOKIE_NAME="general_session", SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    app.register_blueprint(auth)
    app.register_blueprint(board)

    @app.get("/health")
    def health():
        with connect_db() as conn:
            conn.execute("SELECT 1")
        return jsonify(status="ok")
    register_request_logging(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5100, debug=True)
