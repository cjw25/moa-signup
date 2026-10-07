from db import connect_db


def list_notes():
    with connect_db() as conn:
        return conn.execute(
            "SELECT id, title, body, status FROM observation_notes ORDER BY id DESC"
        ).fetchall()


def find_note(note_id):
    with connect_db() as conn:
        return conn.execute(
            "SELECT id, title, body, status FROM observation_notes WHERE id = %s", (note_id,)
        ).fetchone()


def create_note(title, body, status):
    with connect_db() as conn:
        return conn.execute(
            "INSERT INTO observation_notes (title, body, status) VALUES (%s, %s, %s) "
            "RETURNING id, title, body, status",
            (title, body, status),
        ).fetchone()


def update_note(note_id, title, body, status):
    with connect_db() as conn:
        return conn.execute(
            "UPDATE observation_notes SET title = %s, body = %s, status = %s WHERE id = %s "
            "RETURNING id, title, body, status",
            (title, body, status, note_id),
        ).fetchone()


def delete_note(note_id):
    with connect_db() as conn:
        return conn.execute(
            "DELETE FROM observation_notes WHERE id = %s RETURNING id", (note_id,)
        ).fetchone()
