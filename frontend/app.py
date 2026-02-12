import streamlit as st
import pandas as pd
import requests

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
from ui.student_ui import student_login_page, student_menu
from ui.admin_ui import admin_portal_menu
from services.api_client import (
    get_all_events, get_feedback, get_average_rating,
)


# ---------- MAIN MENU ----------
def main_menu():
    st.title("Eventra")
    st.markdown("A Smart Way Of Event Management for Campus Life.")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Student Portal", use_container_width=True):
            st.session_state['page'] = 'student_login'
            st.rerun()

    with col2:
        if st.button("Host / Admin Portal", use_container_width=True):
            st.session_state['page'] = 'admin_portal'
            st.rerun()

    with col3:
        if st.button("View Public Feedback", use_container_width=True):
            st.session_state['page'] = 'view_feedback_public'
            st.rerun()

    st.divider()


# ---------- PUBLIC FEEDBACK ----------
def display_view_event_feedback():
    st.subheader("View Event Feedback")

    try:
        events = get_all_events()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not events:
        st.info("No events available.")
        return

    event_map = {e["id"]: e["name"] for e in events}
    event_ids = [e["id"] for e in events]

    event_id = st.selectbox(
        "Select Event:",
        options=[None] + event_ids,
        format_func=lambda x: event_map.get(x, "Select Event") if x else "Select Event"
    )

    if event_id:
        try:
            feedback = get_feedback(event_id)
        except requests.RequestException:
            feedback = []

        if feedback:
            df = pd.DataFrame(feedback)
            df = df[["student_name", "srn", "rating", "comments"]]
            df.columns = ["Student Name", "SRN", "Rating", "Comment"]
            st.dataframe(df, hide_index=True, use_container_width=True)

        try:
            avg_data = get_average_rating(event_id)
            avg = avg_data.get("average_rating", 0.0)
        except requests.RequestException:
            avg = 0.0

        st.markdown(f"### Average Rating: **{avg:.2f}/5.00**")


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
        if st.button("Back to Main Menu"):
            st.session_state['page'] = 'main'
            st.rerun()


# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    run_app()
