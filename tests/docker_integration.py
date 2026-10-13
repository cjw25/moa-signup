"""Exercise the two independent Compose projects through their public gateways."""

import json
import subprocess
import time

import requests


GENERAL = "http://127.0.0.1:8081"
MONITOR = "http://127.0.0.1:8082"


def run(*args, input_text=None):
    result = subprocess.run(args, input=input_text, text=True, capture_output=True, check=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    return result.stdout


def compose(part, *args, input_text=None):
    return run("docker", "compose", "-f", f"compose-{part}.yaml", *args, input_text=input_text)


def ready(url):
    for _ in range(120):
        try:
            if requests.get(url, timeout=2).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise AssertionError(f"Gateway did not become ready: {url}")


def check(response, status):
    assert response.status_code == status, (response.status_code, response.text)
    return response


def main():
    compose("general", "config", "--quiet")
    compose("monitor", "config", "--quiet")
    run("docker", "network", "create", "m5d1-events")

    compose("monitor", "up", "-d", "--build")
    ready(MONITOR + "/api/health")
    ready(MONITOR)
    compose("monitor", "exec", "-T", "monitor-api", "python", "create_user.py",
            input_text="operator\n운영자\nLearn123!\n")
    monitor = requests.Session()
    check(monitor.get(MONITOR + "/api/auth/me"), 401)
    check(monitor.post(MONITOR + "/api/auth/login", json={"username": "operator", "password": "Learn123!"}), 200)
    check(monitor.get(MONITOR + "/api/auth/me"), 200)

    compose("general", "up", "-d", "--build")
    ready(GENERAL + "/health")
    compose("general", "exec", "-T", "general-api", "python", "create_user.py",
            input_text="student\nLearn123!\n")
    names = json.loads(run("docker", "network", "inspect", "m5d1-events"))[0]["Containers"]
    member_names = {entry["Name"] for entry in names.values()}
    assert any("general-api" in name for name in member_names), member_names
    assert any("monitor-api" in name for name in member_names), member_names
    assert not any("-db-" in name for name in member_names), member_names
    assert compose("general", "exec", "-T", "general-api", "getent", "hosts", "monitor-api").strip()

    board = requests.Session()
    check(board.get(GENERAL, allow_redirects=False), 302)
    check(board.post(GENERAL + "/login", data={"username": "student", "password": "wrong"}), 401)
    check(board.post(GENERAL + "/login", data={"username": "student", "password": "Learn123!"}, allow_redirects=False), 303)
    assert "나만의 게시판" in check(board.get(GENERAL), 200).text
    records = check(monitor.get(MONITOR + "/api/events"), 200).json()
    assert any(e["event_type"] == "login_failure" and e["status_code"] == 401 for e in records)
    assert any(e["event_type"] == "login_success" and e["status_code"] == 200 for e in records)
    note = check(monitor.post(MONITOR + "/api/notes", json={
        "title": "Docker 점검", "body": "로그인 실패와 성공을 확인했다", "status": "확인 전"
    }), 201).json()
    note_id = note["id"]
    assert any(n["id"] == note_id for n in check(monitor.get(MONITOR + "/api/notes"), 200).json())

    compose("general", "down")
    compose("monitor", "down")
    compose("monitor", "up", "-d")
    ready(MONITOR + "/api/health")
    compose("general", "up", "-d")
    ready(GENERAL + "/health")
    again = requests.Session()
    check(again.post(MONITOR + "/api/auth/login", json={"username": "operator", "password": "Learn123!"}), 200)
    assert any(n["id"] == note_id and n["title"] == "Docker 점검" for n in check(again.get(MONITOR + "/api/notes"), 200).json())
    stored = check(again.get(MONITOR + "/api/events"), 200).json()
    assert any(e["event_type"] == "login_failure" for e in stored)
    assert any(e["event_type"] == "login_success" for e in stored)
    compose("monitor", "ps")
    compose("general", "ps")
    print("Docker gateway, shared network, login events, notes, and volume persistence passed")


if __name__ == "__main__":
    main()
