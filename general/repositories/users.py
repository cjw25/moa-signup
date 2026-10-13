from db import connect_db


def find_user(username):
    with connect_db() as conn:
        return conn.execute(
            "SELECT id, username, password_hash FROM general_users WHERE username = %s",
            (username,),
        ).fetchone()
