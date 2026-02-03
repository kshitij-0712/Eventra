import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    layout="wide",
    page_title="Eventra"
)

# ---------- SESSION STATE ----------
if 'logged_in_user_id' not in st.session_state:
    st.session_state['logged_in_user_id'] = None

if 'page' not in st.session_state:
    st.session_state['page'] = 'main'


# ---------- IMPORT UI MODULES ----------
from ui.student_ui import (
    student_login_page,
    student_menu
)

from ui.admin_ui import admin_portal_menu

from utils.helpers import execute_query
import pandas as pd


# ---------- MAIN MENU ----------
def main_menu():
    st.title("Eventra")
    st.markdown(
        "A Smart Way Of Event Management for Campus Life. "
    
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧑‍🎓 Student Portal", use_container_width=True):
            st.session_state['page'] = 'student_login'
            st.rerun()

    with col2:
        if st.button("🧑‍💼 Host / Admin Portal", use_container_width=True):
            st.session_state['page'] = 'admin_portal'
            st.rerun()

    with col3:
        if st.button("📊 View Public Feedback", use_container_width=True):
            st.session_state['page'] = 'view_feedback_public'
            st.rerun()

    st.divider()


# ---------- PUBLIC FEEDBACK ----------
def display_view_event_feedback():
    st.subheader("📊 View Event Feedback")

    events = execute_query("SELECT id, name FROM tbl_events ORDER BY date DESC")
    if not events:
        st.info("No events available.")
        return

    event_map = {e[0]: e[1] for e in events}
    event_ids = [e[0] for e in events]

    event_id = st.selectbox(
        "Select Event:",
        options=[None] + event_ids,
        format_func=lambda x: event_map.get(x, "Select Event") if x else "Select Event"
    )

    if event_id:
        feedback = execute_query(
            """
            SELECT s.name, s.srn, f.rating, f.comments
            FROM tbl_event_feedback f
            JOIN tbl_students s ON f.user_id = s.id
            WHERE f.event_id = %s
            """,
            (event_id,)
        )

        if feedback:
            df = pd.DataFrame(
                feedback,
                columns=["Student Name", "SRN", "Rating", "Comment"]
            )
            st.dataframe(df, hide_index=True, use_container_width=True)

        avg = execute_query(
            "SELECT get_average_rating(%s)",
            (event_id,),
            fetch_type="one"
        )[0] or 0.0

        st.markdown(f"### ⭐ Average Rating: **{avg:.2f}/5.00**")


# ---------- ROUTER ----------
def run_app():
    page = st.session_state['page']

    if page == 'main':
        main_menu()

    elif page == 'student_login':
        student_login_page()

    elif page == 'student_menu':
        student_menu()

    elif page == 'admin_portal':
        admin_portal_menu()

    elif page == 'view_feedback_public':
        display_view_event_feedback()
        if st.button("← Back to Main Menu"):
            st.session_state['page'] = 'main'
            st.rerun()


# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    run_app()
