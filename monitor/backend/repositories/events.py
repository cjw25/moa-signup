from db import connect_db


def list_events():
    with connect_db() as conn:
        return conn.execute(
            "SELECT id, occurred_at, method, path, status_code FROM request_events ORDER BY id DESC"
        ).fetchall()


def create_event(method, path, status_code, occurred_at):
    with connect_db() as conn:
        return conn.execute(
            "INSERT INTO request_events (occurred_at, method, path, status_code) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (occurred_at, method, path, status_code),
        ).fetchone()
