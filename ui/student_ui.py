import streamlit as st
import datetime
import pandas as pd

from db.connection import conn
from utils.helpers import execute_query, commit_transaction
from services.data_fetch_service import list_all_students, list_scheduled_events


# ---------------- LOGIN & MENU ----------------

def student_login_page():
    st.header("🧑‍🎓 Student Login")
    students = list_all_students()

    student_map = {s[0]: f"{s[2]} ({s[1]})" for s in students}
    sid = st.selectbox(
        "Select your Student ID:",
        student_map.keys(),
        format_func=lambda x: student_map[x]
    )

    if st.button("Log In"):
        st.session_state["logged_in_user_id"] = sid
        st.session_state["page"] = "student_menu"
        st.rerun()


def student_menu():
    user_id = st.session_state["logged_in_user_id"]

    result = execute_query(
        "SELECT name FROM tbl_students WHERE id=%s",
        (user_id,),
        fetch_type="one"
    )
    if not result:
        st.error("Student not found. Please log in again.")
        st.session_state["page"] = "main"
        st.session_state["logged_in_user_id"] = None
        st.rerun()
        return

    student_name = result[0]

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
    st.subheader("🎫 My Upcoming Registrations")

    query = """
        SELECT e.id, e.name, e.date, e.start_time, v.name
        FROM tbl_event_participants p
        JOIN tbl_events e ON p.event_id = e.id
        LEFT JOIN tbl_venues v ON e.location_id = v.id
        WHERE p.user_id = %s
          AND (e.date + e.end_time) > NOW()
        ORDER BY e.date
    """
    rows = execute_query(query, (user_id,))
    if not rows:
        st.info("You are not registered for any upcoming events.")
        return False

    df = pd.DataFrame(
        rows,
        columns=["Event ID", "Event Name", "Date", "Start Time", "Venue"],
    )
    st.dataframe(df, hide_index=True, use_container_width=True)
    return True


def display_cancel_registration(user_id):
    st.subheader("🚫 Cancel Registration")

    if not display_my_registrations(user_id):
        return

    query = """
        SELECT e.id, e.name
        FROM tbl_event_participants p
        JOIN tbl_events e ON p.event_id = e.id
        WHERE p.user_id = %s
          AND (e.date + e.end_time) > NOW()
    """
    events = execute_query(query, (user_id,))
    event_map = {e[0]: e[1] for e in events}

    event_id = st.selectbox(
        "Select Event:",
        event_map.keys(),
        format_func=lambda x: event_map[x],
    )

    if st.button("Confirm Cancellation"):
        cursor = None
        try:
            cursor = conn.cursor()

            # Lock the ticket row, then restore quantity
            cursor.execute(
                """
                SELECT id FROM tbl_tickets
                WHERE event_id = %s
                FOR UPDATE
                """,
                (event_id,),
            )

            # Get the ticket id from the student's order for this event
            cursor.execute(
                """
                SELECT o.ticket_id
                FROM tbl_orders o
                JOIN tbl_tickets t ON o.ticket_id = t.id
                WHERE o.user_id = %s AND t.event_id = %s
                """,
                (user_id, event_id),
            )
            order_row = cursor.fetchone()

            if order_row:
                cursor.execute(
                    "UPDATE tbl_tickets SET quantity = quantity + 1 WHERE id=%s",
                    (order_row[0],),
                )

            if order_row:
                cursor.execute(
                    """
                    DELETE FROM tbl_orders
                    WHERE user_id=%s
                      AND ticket_id IN (
                          SELECT id FROM tbl_tickets WHERE event_id=%s
                      )
                    """,
                    (user_id, event_id),
                )

            cursor.execute(
                "DELETE FROM tbl_event_participants WHERE event_id=%s AND user_id=%s",
                (event_id, user_id),
            )

            conn.commit()
            st.success("Registration cancelled successfully.")
        except Exception as e:
            conn.rollback()
            st.error(f"Cancellation failed: {e}")
        finally:
            if cursor:
                cursor.close()


def display_register_event(user_id):
    st.subheader("🎟️ Register for Event")

    events = list_scheduled_events()
    if not events:
        st.info("No upcoming events.")
        return

    event_map = {e[0]: f"{e[1]} at {e[6]}" for e in events}
    event_id = st.selectbox(
        "Select Event:",
        event_map.keys(),
        format_func=lambda x: event_map[x],
    )

    existing = execute_query(
        """
        SELECT 1
        FROM tbl_event_participants
        WHERE event_id=%s AND user_id=%s
        """,
        (event_id, user_id),
        fetch_type="one",
    )
    if existing:
        st.info("You are already registered for this event.")
        return

    tickets = execute_query(
        """
        SELECT id, ticket_type, price, quantity
        FROM tbl_tickets
        WHERE event_id=%s AND quantity>0
        """,
        (event_id,),
    )

    if not tickets:
        st.warning("No tickets available.")
        return

    ticket_map = {t[0]: t for t in tickets}
    ticket_id = st.selectbox(
        "Select Ticket:",
        ticket_map.keys(),
        format_func=lambda x: f"{ticket_map[x][1]} - ₹{ticket_map[x][2]}",
    )

    price = ticket_map[ticket_id][2]
    st.write(f"Price: ₹{price}")

    if st.button("Confirm Order and Register"):
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1
                FROM tbl_event_participants
                WHERE event_id=%s AND user_id=%s
                """,
                (event_id, user_id),
            )
            if cursor.fetchone():
                st.info("You are already registered for this event.")
                conn.rollback()
                return

            cursor.execute(
                "SELECT quantity FROM tbl_tickets WHERE id=%s FOR UPDATE",
                (ticket_id,),
            )

            available = cursor.fetchone()[0]
            if available < 1:
                st.error("Tickets sold out. Try another ticket type.")
                conn.rollback()
                return

            cursor.execute(
                "UPDATE tbl_tickets SET quantity = quantity - 1 WHERE id=%s",
                (ticket_id,),
            )

            cursor.execute(
                """
                INSERT INTO tbl_orders
                (ticket_id, user_id, order_time, payment_status)
                VALUES (%s,%s,%s,'Completed')
                """,
                (ticket_id, user_id, datetime.datetime.now()),
            )

            cursor.execute(
                """
                INSERT INTO tbl_event_participants
                (event_id, user_id, registration_time)
                VALUES (%s,%s,%s)
                """,
                (event_id, user_id, datetime.datetime.now()),
            )

            conn.commit()
            st.success("Successfully registered!")
        except Exception as e:
            conn.rollback()
            st.error(e)
        finally:
            if cursor:
                cursor.close()


def display_list_completed_events():
    st.subheader("🏁 Completed Events")

    query = """
        SELECT e.id, e.name, e.date, v.name, h.name
        FROM tbl_events e
        LEFT JOIN tbl_venues v ON e.location_id = v.id
        LEFT JOIN tbl_hosts h ON e.organizer_id = h.id
        WHERE (e.date + e.end_time) <= NOW()
        ORDER BY e.date DESC
    """
    rows = execute_query(query)
    if not rows:
        st.info("No completed events.")
        return False

    df = pd.DataFrame(
        rows,
        columns=["ID", "Name", "Date", "Venue", "Organizer"],
    )
    st.dataframe(df, hide_index=True, use_container_width=True)
    return True


def display_write_event_feedback(user_id):
    st.subheader("✍️ Write Feedback")

    if not display_list_completed_events():
        return

    events = execute_query(
        "SELECT id, name FROM tbl_events WHERE (date + end_time) <= NOW()"
    )
    event_map = {e[0]: e[1] for e in events}

    event_id = st.selectbox(
        "Select Event:",
        event_map.keys(),
        format_func=lambda x: event_map[x],
    )

    part = execute_query(
        """
        SELECT attendance_status
        FROM tbl_event_participants
        WHERE event_id=%s AND user_id=%s
        """,
        (event_id, user_id),
        fetch_type="one",
    )

    if not part or part[0] is False:
        st.error("Attendance not marked.")
        return

    feedback = execute_query(
        """
        SELECT id
        FROM tbl_event_feedback
        WHERE event_id=%s AND user_id=%s
        """,
        (event_id, user_id),
        fetch_type="one",
    )

    if feedback:
        st.info("Feedback already submitted.")
        return

    with st.form("feedback_form"):
        rating = st.slider("Rating", 1, 5, 5)
        comments = st.text_area("Comments")
        if st.form_submit_button("Submit"):
            result = commit_transaction(
                """
                INSERT INTO tbl_event_feedback
                (event_id, user_id, rating, comments, submitted_at)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (event_id, user_id, rating, comments, datetime.datetime.now()),
            )
            if result is True:
                st.success("Feedback submitted.")
                st.rerun()
            else:
                st.error(result)
