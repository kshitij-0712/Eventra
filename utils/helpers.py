import streamlit as st
import mysql.connector
from mysql.connector import errorcode
import datetime

from db.connection import conn


def convert_to_time(td):
    """
    Converts datetime.timedelta (returned by MySQL for TIME column) 
    to datetime.time, which st.time_input requires.
    """
    if isinstance(td, datetime.timedelta):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return datetime.time(hours, minutes, seconds)
    elif isinstance(td, datetime.time):
        return td
    elif isinstance(td, str):
        try:
            h, m, s = map(int, td.split(':'))
            return datetime.time(h, m, s)
        except:
            pass
    return datetime.time(0, 0, 0)


def execute_query(query, params=None, fetch_type='all'):
    """Utility to safely execute SELECT queries and return data."""
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute(query, params)
        
        if fetch_type == 'one':
            result = cursor.fetchone()
        elif fetch_type == 'all':
            result = cursor.fetchall()
        else:
            result = True 
            
        cursor.close()
        return result
    except mysql.connector.Error as err:
        st.error(f"Database Read Error: {err.msg}")
        return None


def commit_transaction(sql, val):
    """Utility to perform INSERT/UPDATE/DELETE with commit/rollback."""
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except mysql.connector.Error as err:
        conn.rollback()
        cursor.close()
        if err.errno == errorcode.ER_DUP_ENTRY:
            return "Duplicate entry error."
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            return "Foreign key constraint failed (Invalid ID)."
        else:
            return f"Database Write Error: {err.msg}"
    except Exception as e:
        conn.rollback()
        return f"Unexpected Error: {e}"
