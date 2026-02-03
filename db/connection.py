import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("SUPABASE_DB_HOST"),
    "dbname": os.getenv("SUPABASE_DB_NAME"),
    "user": os.getenv("SUPABASE_DB_USER"),
    "password": os.getenv("SUPABASE_DB_PASSWORD"),
    "port": os.getenv("SUPABASE_DB_PORT", "5432"),
}

@st.cache_resource(ttl=3600)
def init_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except psycopg2.Error as err:
        st.error(f"Supabase DB connection error: {err}")
        st.stop()

conn = init_connection()
