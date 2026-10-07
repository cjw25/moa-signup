import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    return psycopg.connect(os.environ["DATABASE_URL"])
