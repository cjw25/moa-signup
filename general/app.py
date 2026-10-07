from flask import Flask

from request_logging import register_request_logging
from routes.posts import board


def create_app():
    app = Flask(__name__)
    app.register_blueprint(board)
    register_request_logging(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
