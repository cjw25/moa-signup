from flask import Flask, jsonify, request

app = Flask(__name__)
events = []


@app.post("/events")
def receive_event():
    event = request.get_json(silent=True)
    if not isinstance(event, dict):
        return jsonify(error="JSON 객체가 필요합니다."), 400
    events.append(event)
    return "", 204


@app.get("/events")
def list_events():
    return jsonify(events)


if __name__ == "__main__":
    app.run(port=5001)
