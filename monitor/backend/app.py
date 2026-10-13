import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from db import connect_db
from routes.auth import auth
from routes.events import events
from routes.notes import notes


def create_app():
    load_dotenv()
    app = Flask(__name__)
    secret = os.environ.get("MONITOR_SECRET_KEY")
    if not secret or secret == "REPLACE_WITH_A_LONG_RANDOM_HEX_VALUE":
        raise RuntimeError("MONITOR_SECRET_KEY를 .env에 설정해 주세요.")
    app.secret_key = secret
    app.config.update(SESSION_COOKIE_NAME="monitor_session", SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    app.register_blueprint(auth)
    app.register_blueprint(events)
    app.register_blueprint(notes)

    @app.get("/api/health")
    def health():
        with connect_db() as conn:
            conn.execute("SELECT 1")
        return jsonify(status="ok")
    return app


if __name__ == "__main__":
    create_app().run(port=5200, debug=True)
