from db import connect_db


def list_events(path="", status=None):
    clauses = []
    params = []
    if path:
        clauses.append("path ILIKE %s")
        params.append(f"%{path}%")
    if status is not None:
        clauses.append("status_code = %s")
        params.append(status)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with connect_db() as conn:
        return conn.execute(
            "SELECT id, occurred_at, method, path, status_code FROM request_events"
            + where + " ORDER BY id DESC", params
        ).fetchall()


def create_event(method, path, status_code, occurred_at):
    with connect_db() as conn:
        return conn.execute(
            "INSERT INTO request_events (occurred_at, method, path, status_code) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (occurred_at, method, path, status_code),
        ).fetchone()
