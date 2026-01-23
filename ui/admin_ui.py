import streamlit as st
import datetime
import pandas as pd

from db.connection import conn
from utils.helpers import execute_query, commit_transaction, convert_to_time
from services.data_fetch_service import (
    list_all_hosts,
    list_all_venues,
    list_available_venues,
    list_scheduled_events,
    list_all_resources
)

# ---------- ADMIN MENU ----------

def admin_portal_menu():
    st.sidebar.title("Host/Admin Menu")
    st.sidebar.button(
        "Log Out",
        on_click=lambda: (st.session_state.update({'page': 'main', 'logged_in_user_id': None}), st.rerun()),
        use_container_width=True
    )

    st.header("🧑‍💼 Host & Admin Dashboard")

    choice = st.sidebar.radio(
        "Admin Tasks",
        (
            'Add New Event',
            'Update Event Details',
            'Manage Event Tickets',
            'Mark Event Attendance',
            'View Participants',
            'Add New Student',
            'View Students/Hosts',
            'Manage Venues',
            'Manage Resources'
        )
    )

    if choice == 'Add New Event':
        display_add_new_event()
    elif choice == 'Update Event Details':
        display_update_event_details()
    elif choice == 'Manage Event Tickets':
        display_manage_event_tickets()
    elif choice == 'Mark Event Attendance':
        display_mark_attendance()
    elif choice == 'View Participants':
        display_view_participants()
    elif choice == 'Add New Student':
        display_add_new_student()
    elif choice == 'View Students/Hosts':
        display_view_users()
    elif choice == 'Manage Venues':
        display_manage_venues()
    elif choice == 'Manage Resources':
        display_manage_resources()


# ---------- ADMIN FUNCTIONS ----------

def display_add_new_student():
    st.subheader("🧑‍🎓 Add New Student")

    with st.form("add_student"):
        srn = st.text_input("SRN")
        name = st.text_input("Name")
        sem = st.number_input("Semester", 1, 8, 1)
        sec = st.text_input("Section")
        if st.form_submit_button("Add"):
            result = commit_transaction(
                "INSERT INTO tbl_students (srn,name,semester,section) VALUES (%s,%s,%s,%s)",
                (srn, name, sem, sec)
            )
            if result is True:
                st.success("Student added.")
            else:
                st.error(result)


def display_add_new_event():
    st.subheader("🗓️ Add New Event")

    hosts = list_all_hosts()
    venues = list_available_venues()
    if not hosts or not venues:
        st.warning("Hosts or venues missing.")
        return

    host_map = {h[0]: h[1] for h in hosts}
    venue_map = {v[0]: f"{v[1]} ({v[3]})" for v in venues}

    with st.form("add_event"):
        name = st.text_input("Event Name")
        desc = st.text_area("Description")
        date = st.date_input("Date", datetime.date.today())
        start = st.time_input("Start", datetime.time(10, 0))
        end = st.time_input("End", datetime.time(12, 0))
        host_id = st.selectbox("Host", host_map.keys(), format_func=lambda x: host_map[x])
        venue_id = st.selectbox("Venue", venue_map.keys(), format_func=lambda x: venue_map[x])
        maxp = st.number_input("Max Participants", 1, venue_map and 100, 50)

        if st.form_submit_button("Create"):
            result = commit_transaction(
                """
                INSERT INTO tbl_events
                (name,description,date,start_time,end_time,location_id,organizer_id,status,max_participants)
                VALUES (%s,%s,%s,%s,%s,%s,%s,'Scheduled',%s)
                """,
                (name, desc, date, start, end, venue_id, host_id, maxp)
            )
            if result is True:
                st.success("Event created.")
            else:
                st.error(result)


def display_update_event_details():
    st.subheader("✏️ Update Event")

    events = list_scheduled_events()
    if not events:
        st.info("No events.")
        return

    event_map = {e[0]: e[1] for e in events}
    eid = st.selectbox("Event", event_map.keys(), format_func=lambda x: event_map[x])

    cursor = conn.cursor(buffered=True)
    cursor.execute("SELECT * FROM tbl_events WHERE id=%s", (eid,))
    ev = cursor.fetchone()
    cursor.close()

    (_, name, desc, date, start, end, loc, org, status, maxp, *_) = ev

    with st.form("update_event"):
        n_name = st.text_input("Name", name)
        n_desc = st.text_area("Description", desc)
        n_date = st.date_input("Date", date)
        n_start = st.time_input("Start", convert_to_time(start))
        n_end = st.time_input("End", convert_to_time(end))
        if st.form_submit_button("Update"):
            result = commit_transaction(
                """
                UPDATE tbl_events SET name=%s,description=%s,date=%s,start_time=%s,end_time=%s
                WHERE id=%s
                """,
                (n_name, n_desc, n_date, n_start, n_end, eid)
            )
            if result is True:
                st.success("Updated.")
            else:
                st.error(result)


def display_manage_event_tickets():
    st.subheader("🎫 Manage Tickets")

    events = execute_query("SELECT id,name FROM tbl_events")
    event_map = {e[0]: e[1] for e in events}
    eid = st.selectbox("Event", event_map.keys(), format_func=lambda x: event_map[x])

    tickets = execute_query(
        "SELECT id,ticket_type,price,quantity FROM tbl_tickets WHERE event_id=%s",
        (eid,)
    )

    if tickets:
        st.dataframe(pd.DataFrame(tickets, columns=["ID","Type","Price","Qty"]), hide_index=True)

    with st.form("add_ticket"):
        ttype = st.text_input("Ticket Type")
        price = st.number_input("Price", 0.0)
        qty = st.number_input("Quantity", 0)
        if st.form_submit_button("Add"):
            result = commit_transaction(
                "INSERT INTO tbl_tickets (event_id,ticket_type,price,quantity) VALUES (%s,%s,%s,%s)",
                (eid, ttype, price, qty)
            )
            if result is True:
                st.success("Ticket added.")
            else:
                st.error(result)


def display_mark_attendance():
    st.subheader("🧑‍💼 Mark Attendance")

    events = execute_query("SELECT id,name FROM tbl_events")
    event_map = {e[0]: e[1] for e in events}
    eid = st.selectbox("Event", event_map.keys(), format_func=lambda x: event_map[x])

    parts = execute_query(
        """
        SELECT s.id,s.name,s.srn,p.attendance_status
        FROM tbl_event_participants p
        JOIN tbl_students s ON p.user_id=s.id
        WHERE p.event_id=%s
        """,
        (eid,)
    )

    if not parts:
        st.info("No participants.")
        return

    st.dataframe(pd.DataFrame(parts, columns=["ID","Name","SRN","Attended"]), hide_index=True)

    sid = st.selectbox("Student ID", [p[0] for p in parts])
    if st.button("Mark Attended"):
        result = commit_transaction(
            "UPDATE tbl_event_participants SET attendance_status=1 WHERE event_id=%s AND user_id=%s",
            (eid, sid)
        )
        if result is True:
            st.success("Marked attended.")
        else:
            st.error(result)


def display_view_participants():
    st.subheader("👥 Participants")

    rows = execute_query("""
        SELECT e.name,s.name,s.srn,p.attendance_status
        FROM tbl_event_participants p
        JOIN tbl_events e ON p.event_id=e.id
        JOIN tbl_students s ON p.user_id=s.id
    """)

    if rows:
        st.dataframe(pd.DataFrame(rows, columns=["Event","Student","SRN","Attended"]), hide_index=True)
    else:
        st.info("No data.")


def display_view_users():
    st.subheader("👤 Users")

    students = execute_query("SELECT id,srn,name,semester,section FROM tbl_students")
    hosts = list_all_hosts()

    st.markdown("### Students")
    if students:
        st.dataframe(pd.DataFrame(students, columns=["ID","SRN","Name","Sem","Sec"]), hide_index=True)

    st.markdown("### Hosts")
    if hosts:
        st.dataframe(pd.DataFrame(hosts, columns=["ID","Name","Dept","Role"]), hide_index=True)


def display_manage_venues():
    st.subheader("🏟️ Venues")

    venues = list_all_venues()
    df = pd.DataFrame(venues, columns=["ID","Name","Building","Capacity","Available"])
    st.dataframe(df, hide_index=True)

    vid = st.selectbox("Venue ID", [v[0] for v in venues])
    status = st.radio("Availability", [1,0])
    if st.button("Update"):
        result = commit_transaction(
            "UPDATE tbl_venues SET is_available=%s WHERE id=%s",
            (status, vid)
        )
        if result is True:
            st.success("Updated.")
        else:
            st.error(result)


def display_manage_resources():
    st.subheader("📦 Resources")

    resources = list_all_resources()
    if resources:
        st.dataframe(pd.DataFrame(resources, columns=["ID","Name","Type","Qty","Status"]), hide_index=True)
