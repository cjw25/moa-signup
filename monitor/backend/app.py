import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from db import connect_db
from routes.auth import auth
from routes.events import events
from routes.notes import notes
from observability import init_observability


def create_app():
    load_dotenv()
    app = Flask(__name__)
    secret = os.getenv("SECRET_KEY") or os.getenv("MONITOR_SECRET_KEY")
    if not secret or secret == "REPLACE_WITH_A_LONG_RANDOM_HEX_VALUE":
        raise RuntimeError("SECRET_KEY를 .env에 설정해 주세요.")
    app.secret_key = secret
    app.config.update(SESSION_COOKIE_NAME="monitor_session", SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true")
    init_observability("mini-monitor")
    app.register_blueprint(auth)
    app.register_blueprint(events)
    app.register_blueprint(notes)

    @app.get("/health")
    @app.get("/api/health")
    def health():
        return jsonify(status="ok")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5200, debug=True)
