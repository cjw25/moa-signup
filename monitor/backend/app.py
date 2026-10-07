from flask import Flask

from routes.auth import auth
from routes.events import events
from routes.notes import notes


def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth)
    app.register_blueprint(events)
    app.register_blueprint(notes)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5200, debug=True)
