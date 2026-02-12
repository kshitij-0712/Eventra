import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("SUPABASE_DB_HOST"),
    "dbname": os.getenv("SUPABASE_DB_NAME"),
    "user": os.getenv("SUPABASE_DB_USER"),
    "password": os.getenv("SUPABASE_DB_PASSWORD"),
    "port": os.getenv("SUPABASE_DB_PORT", "5432"),
    "sslmode": "require"
}


def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    return conn


@contextmanager
def get_cursor(commit=False):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
