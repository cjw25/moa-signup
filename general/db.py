import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    if os.getenv("DB_HOST"):
        return psycopg.connect(
            host=os.environ["DB_HOST"], port=os.getenv("DB_PORT", "5432"),
            dbname=os.environ["DB_NAME"], user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"], sslmode=os.getenv("DB_SSLMODE", "require"),
        )
    return psycopg.connect(os.environ["DATABASE_URL"])
