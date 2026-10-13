from db import connect_db
from psycopg.rows import dict_row


def find_user(username):
    with connect_db() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            return cursor.execute(
                "SELECT id, username, password_hash FROM general_users WHERE username = %s",
                (username,),
            ).fetchone()
