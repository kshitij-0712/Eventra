import streamlit as st
import pandas as pd
import requests

from services.api_client import (
    get_students, get_student,
    get_scheduled_events, get_completed_events,
    get_tickets, get_user_registrations,
    register_for_event, cancel_registration,
    submit_feedback, get_feedback, get_average_rating,
)


# ---------------- LOGIN & MENU ----------------

def student_login_page():
    st.header("Student Login")

    try:
        students = get_students()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    student_map = {s["id"]: f"{s['name']} ({s['srn']})" for s in students}
    sid = st.selectbox(
        "Select your Student ID:",
        list(student_map.keys()),
        format_func=lambda x: student_map[x]
    )

    if st.button("Log In"):
        st.session_state["logged_in_user_id"] = sid
        st.session_state["page"] = "student_menu"
        st.rerun()


def student_menu():
    user_id = st.session_state["logged_in_user_id"]

    try:
        student = get_student(user_id)
    except requests.HTTPError:
        st.error("Student not found. Please log in again.")
        st.session_state["page"] = "main"
        st.session_state["logged_in_user_id"] = None
        st.rerun()
        return

    student_name = student["name"]

    st.sidebar.title(f"Welcome, {student_name}!")
    st.sidebar.button(
        "Log Out",
        on_click=lambda: st.session_state.update(
            {"page": "main", "logged_in_user_id": None}
        )
    )

    choice = st.sidebar.radio(
        "Menu",
        (
            "My Registrations",
            "Register for Event",
            "Completed Events",
            "Write Feedback",
            "Cancel Registration",
        )
    )

    if choice == "My Registrations":
        display_my_registrations(user_id)
    elif choice == "Register for Event":
        display_register_event(user_id)
    elif choice == "Completed Events":
        display_list_completed_events()
    elif choice == "Write Feedback":
        display_write_event_feedback(user_id)
    elif choice == "Cancel Registration":
        display_cancel_registration(user_id)


# ---------------- STUDENT FEATURES ----------------

def display_my_registrations(user_id):
    st.subheader("My Upcoming Registrations")

    try:
        rows = get_user_registrations(user_id)
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not rows:
        st.info("You are not registered for any upcoming events.")
        return False

    df = pd.DataFrame(rows)
    df = df[["event_id", "event_name", "date", "start_time", "venue_name"]]
    df.columns = ["Event ID", "Event Name", "Date", "Start Time", "Venue"]
    st.dataframe(df, hide_index=True, use_container_width=True)
    return True


def display_cancel_registration(user_id):
    st.subheader("Cancel Registration")

    try:
        regs = get_user_registrations(user_id)
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not regs:
        st.info("You are not registered for any upcoming events.")
        return

    # Show current registrations
    df = pd.DataFrame(regs)
    df = df[["event_id", "event_name", "date", "start_time", "venue_name"]]
    df.columns = ["Event ID", "Event Name", "Date", "Start Time", "Venue"]
    st.dataframe(df, hide_index=True, use_container_width=True)

    event_map = {r["event_id"]: r["event_name"] for r in regs}
    event_id = st.selectbox(
        "Select Event:",
        list(event_map.keys()),
        format_func=lambda x: event_map[x],
    )

    if st.button("Confirm Cancellation"):
        try:
            cancel_registration(event_id, user_id)
            st.success("Registration cancelled successfully.")
            st.rerun()
        except requests.HTTPError as e:
            st.error(f"Cancellation failed: {e.response.text}")


def display_register_event(user_id):
    st.subheader("Register for Event")

    try:
        events = get_scheduled_events()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not events:
        st.info("No upcoming events.")
        return

    event_map = {e["id"]: f"{e['name']} at {e.get('venue_name', 'TBD')}"
                 for e in events}
    event_id = st.selectbox(
        "Select Event:",
        list(event_map.keys()),
        format_func=lambda x: event_map[x],
    )

    # Get available tickets
    try:
        tickets = get_tickets(event_id)
        available_tickets = [t for t in tickets if t["quantity"] > 0]
    except requests.RequestException:
        available_tickets = []

    if not available_tickets:
        st.warning("No tickets available.")
        return

    ticket_map = {t["id"]: t for t in available_tickets}
    ticket_id = st.selectbox(
        "Select Ticket:",
        list(ticket_map.keys()),
        format_func=lambda x: f"{ticket_map[x]['ticket_type']} - Rs.{ticket_map[x]['price']}",
    )

    price = ticket_map[ticket_id]["price"]
    st.write(f"Price: Rs.{price}")

    if st.button("Confirm Order and Register"):
        try:
            register_for_event(event_id, user_id, ticket_id)
            st.success("Successfully registered!")
            st.rerun()
        except requests.HTTPError as e:
            error_detail = e.response.json().get("detail", e.response.text)
            if "Already registered" in str(error_detail):
                st.info("You are already registered for this event.")
            elif "sold out" in str(error_detail).lower():
                st.error("Tickets sold out. Try another ticket type.")
            else:
                st.error(f"Registration failed: {error_detail}")


def display_list_completed_events():
    st.subheader("Completed Events")

    try:
        rows = get_completed_events()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not rows:
        st.info("No completed events.")
        return False

    df = pd.DataFrame(rows)
    df = df[["id", "name", "date", "venue_name", "host_name"]]
    df.columns = ["ID", "Name", "Date", "Venue", "Organizer"]
    st.dataframe(df, hide_index=True, use_container_width=True)
    return True


def display_write_event_feedback(user_id):
    st.subheader("Write Feedback")

    try:
        completed = get_completed_events()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not completed:
        st.info("No completed events.")
        return

    # Show completed events
    df = pd.DataFrame(completed)
    df = df[["id", "name", "date", "venue_name", "host_name"]]
    df.columns = ["ID", "Name", "Date", "Venue", "Organizer"]
    st.dataframe(df, hide_index=True, use_container_width=True)

    event_map = {e["id"]: e["name"] for e in completed}
    event_id = st.selectbox(
        "Select Event:",
        list(event_map.keys()),
        format_func=lambda x: event_map[x],
    )

    with st.form("feedback_form"):
        rating = st.slider("Rating", 1, 5, 5)
        comments = st.text_area("Comments")
        if st.form_submit_button("Submit"):
            try:
                submit_feedback(event_id, user_id, rating, comments)
                st.success("Feedback submitted.")
                st.rerun()
            except requests.HTTPError as e:
                error_detail = e.response.json().get("detail", e.response.text)
                if "Attendance not marked" in str(error_detail):
                    st.error("Attendance not marked.")
                elif "already submitted" in str(error_detail).lower():
                    st.info("Feedback already submitted.")
                else:
                    st.error(f"Failed: {error_detail}")
