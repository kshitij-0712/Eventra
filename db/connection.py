import streamlit as st
import mysql.connector
from mysql.connector import errorcode

# IMPORTANT: Replace with your actual MySQL credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "pesu_proj"
}

@st.cache_resource(ttl=3600)
def init_connection():
    """Initializes and caches the database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if not conn.is_connected():
            raise Exception("Connection failed after initialization.")
        return conn
    except mysql.connector.Error as err:
        st.error(f"Error connecting to database: {err.msg}")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during database connection: {e}")
        st.stop()

# Initialize connection once
conn = init_connection()
