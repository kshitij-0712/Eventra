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
        on_click=lambda: st.session_state.update(
            {"page": "main", "logged_in_user_id": None}
        ),
        use_container_width=True,
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
            st.success("Student added.") if result is True else st.error(result)


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
        maxp = st.number_input("Max Participants", 1, 100, 50)

        if st.form_submit_button("Create"):
            result = commit_transaction(
                """
                INSERT INTO tbl_events
                (name,description,date,start_time,end_time,location_id,organizer_id,status,max_participants)
                VALUES (%s,%s,%s,%s,%s,%s,%s,'Scheduled',%s)
                """,
                (name, desc, date, start, end, venue_id, host_id, maxp)
            )
            st.success("Event created.") if result is True else st.error(result)


def display_update_event_details():
    st.subheader("✏️ Update Event")

    events = list_scheduled_events()
    if not events:
        st.info("No upcoming events.")
        return

    event_map = {e[0]: e[1] for e in events}
    eid = st.selectbox("Event", event_map.keys(), format_func=lambda x: event_map[x])

    ev = execute_query(
        "SELECT name, description, date, start_time, end_time FROM tbl_events WHERE id=%s",
        (eid,),
        fetch_type="one",
    )
    if not ev:
        st.error("Event not found.")
        return

    name, desc, date, start, end = ev

    with st.form("update_event"):
        n_name = st.text_input("Name", name)
        n_desc = st.text_area("Description", desc)
        n_date = st.date_input("Date", date)
        n_start = st.time_input("Start", convert_to_time(start))
        n_end = st.time_input("End", convert_to_time(end))
        if st.form_submit_button("Update"):
            result = commit_transaction(
                """
                UPDATE tbl_events
                SET name=%s,description=%s,date=%s,start_time=%s,end_time=%s
                WHERE id=%s
                """,
                (n_name, n_desc, n_date, n_start, n_end, eid)
            )
            st.success("Updated.") if result is True else st.error(result)


def display_manage_event_tickets():
    st.subheader("🎫 Manage Tickets")

    events = execute_query("SELECT id,name FROM tbl_events")
    if not events:
        st.info("No events found.")
        return
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
            st.success("Ticket added.") if result is True else st.error(result)


def display_mark_attendance():
    st.subheader("🧑‍💼 Mark Attendance")

    events = execute_query("SELECT id,name FROM tbl_events")
    if not events:
        st.info("No events found.")
        return
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
            "UPDATE tbl_event_participants SET attendance_status=TRUE WHERE event_id=%s AND user_id=%s",
            (eid, sid)
        )
        st.success("Marked attended.") if result is True else st.error(result)


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
    status_bool = True if status == 1 else False

    if st.button("Update"):
        result = commit_transaction(
            "UPDATE tbl_venues SET is_available=%s WHERE id=%s",
            (status_bool, vid)
        )
        st.success("Updated.") if result is True else st.error(result)


def display_manage_resources():
    st.subheader("📦 Resource Management")

    resources = list_all_resources()
    if not resources:
        st.info("No resources.")
        return

    st.dataframe(
        pd.DataFrame(resources, columns=["ID","Name","Type","Quantity","Status"]),
        hide_index=True
    )

    st.markdown("---")
    st.markdown("### 🔗 Assign Resource to Event")

    events = execute_query(
        "SELECT id, name FROM tbl_events WHERE (date + end_time) > NOW()"
    )
    if not events:
        st.info("No upcoming events.")
        return

    event_map = {e[0]: e[1] for e in events}
    resource_map = {r[0]: f"{r[1]} ({r[3]} available)" for r in resources}

    event_id = st.selectbox("Select Event", event_map.keys(), format_func=lambda x: event_map[x])
    resource_id = st.selectbox("Select Resource", resource_map.keys(), format_func=lambda x: resource_map[x])
    qty = st.number_input("Quantity to Assign", min_value=1, value=1)

    col1, col2 = st.columns(2)
    start_date = col1.date_input("Booking Start Date", key="book_start_date")
    start_time = col1.time_input("Booking Start Time", datetime.time(9, 0), key="book_start_time")
    end_date = col2.date_input("Booking End Date", key="book_end_date")
    end_time = col2.time_input("Booking End Time", datetime.time(17, 0), key="book_end_time")

    if st.button("Assign Resource"):
        start_dt = datetime.datetime.combine(start_date, start_time)
        end_dt = datetime.datetime.combine(end_date, end_time)
        if end_dt <= start_dt:
            st.error("Booking end must be after start.")
            return

        cur = None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO tbl_event_resources
                (event_id, resource_id, quantity_booked, booking_start, booking_end)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (event_id, resource_id, qty, start_dt, end_dt)
            )
            conn.commit()
            st.success("Resource assigned.")
        except Exception as e:
            conn.rollback()
            st.error(e)
        finally:
            if cur:
                cur.close()

    st.markdown("---")
    st.markdown("### 🧹 Replenish Expired Resource Bookings")

    if st.button("Run Replenish Resources"):
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT replenish_resources()")
            restored = cur.fetchone()[0]
            conn.commit()

            if restored > 0:
                st.success(f"Resources replenished: {restored}")
            else:
                st.info("No resources needed replenishment.")
        except Exception as e:
            conn.rollback()
            st.error(e)
        finally:
            if cur:
                cur.close()

    st.markdown("---")
    st.markdown("### 🛠️ Schedule Resource Maintenance")

    res_map = {r[0]: r[1] for r in resources}
    res_id = st.selectbox("Resource", res_map.keys(), format_func=lambda x: res_map[x])

    col1, col2 = st.columns(2)
    m_start_date = col1.date_input("Maintenance Start Date", key="maint_start_date")
    m_start_time = col1.time_input("Maintenance Start Time", datetime.time(9, 0), key="maint_start_time")
    m_end_date = col2.date_input("Maintenance End Date", key="maint_end_date")
    m_end_time = col2.time_input("Maintenance End Time", datetime.time(17, 0), key="maint_end_time")

    reason = st.text_input("Reason")

    if st.button("Start Maintenance"):
        m_start = datetime.datetime.combine(m_start_date, m_start_time)
        m_end = datetime.datetime.combine(m_end_date, m_end_time)
        if m_end <= m_start:
            st.error("Maintenance end must be after start.")
            return

        result = commit_transaction(
            """
            INSERT INTO tbl_resource_maintenance
            (resource_id, maintenance_start, maintenance_end, description)
            VALUES (%s,%s,%s,%s)
            """,
            (res_id, m_start, m_end, reason)
        )

        st.success("Resource sent to maintenance.") if result is True else st.error(result)

