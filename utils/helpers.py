import streamlit as st
import datetime
from db.connection import conn


def convert_to_time(value):
    if isinstance(value, datetime.time):
        return value

    if isinstance(value, datetime.timedelta):
        total = int(value.total_seconds())
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        return datetime.time(hours, minutes, seconds)

    if isinstance(value, str):
        try:
            h, m, s = map(int, value.split(":"))
            return datetime.time(h, m, s)
        except ValueError:
            pass

    return datetime.time(0, 0)


def execute_query(query, params=None, fetch_type="all"):
    """
    Executes SELECT queries safely.
    IMPORTANT: Rolls back on error to avoid
    'current transaction is aborted' state in PostgreSQL.
    """
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(query, params)

        if fetch_type == "one":
            result = cur.fetchone()
        else:
            result = cur.fetchall()

        return result

    except Exception as e:
        conn.rollback()   # 🔴 CRITICAL FIX
        st.error(f"Database Read Error: {e}")
        return None

    finally:
        if cur:
            cur.close()


def commit_transaction(sql, params):
    """
    Executes INSERT / UPDATE / DELETE safely.
    Always commits or rolls back.
    """
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        return str(e)

    finally:
        if cur:
            cur.close()
