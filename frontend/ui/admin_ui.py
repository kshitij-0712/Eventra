import streamlit as st
import pandas as pd
import requests

from services.api_client import (
    get_scheduled_events, get_completed_events, get_all_events,
    get_available_venues, get_venues, get_tickets, get_resources,
    get_hosts, get_participants, get_all_participants,
    create_event, update_event, create_ticket, create_student,
    mark_attendance, update_venue,
    assign_resource, replenish_resources, schedule_maintenance,
)
import datetime


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

    st.header("Host & Admin Dashboard")

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
    st.subheader("Add New Student")

    with st.form("add_student"):
        srn = st.text_input("SRN")
        name = st.text_input("Name")
        sem = st.number_input("Semester", 1, 8, 1)
        sec = st.text_input("Section")
        if st.form_submit_button("Add"):
            try:
                create_student(srn, name, sem, sec)
                st.success("Student added.")
            except requests.HTTPError as e:
                st.error(f"Failed: {e.response.text}")


def display_add_new_event():
    st.subheader("Add New Event")

    try:
        hosts = get_hosts()
        venues = get_available_venues()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not hosts or not venues:
        st.warning("Hosts or venues missing.")
        return

    host_map = {h["id"]: h["name"] for h in hosts}
    venue_map = {v["id"]: f"{v['name']} ({v['capacity']})" for v in venues}

    with st.form("add_event"):
        name = st.text_input("Event Name")
        desc = st.text_area("Description")
        date = st.date_input("Date", datetime.date.today())
        start = st.time_input("Start", datetime.time(10, 0))
        end = st.time_input("End", datetime.time(12, 0))
        host_id = st.selectbox(
            "Host", list(host_map.keys()),
            format_func=lambda x: host_map[x]
        )
        venue_id = st.selectbox(
            "Venue", list(venue_map.keys()),
            format_func=lambda x: venue_map[x]
        )
        maxp = st.number_input("Max Participants", 1, 100, 50)

        if st.form_submit_button("Create"):
            try:
                create_event(name, desc, date, start, end,
                             venue_id, host_id, maxp)
                st.success("Event created.")
            except requests.HTTPError as e:
                st.error(f"Failed: {e.response.text}")


def display_update_event_details():
    st.subheader("Update Event")

    try:
        events = get_scheduled_events()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not events:
        st.info("No upcoming events.")
        return

    event_map = {e["id"]: e["name"] for e in events}
    eid = st.selectbox("Event", list(event_map.keys()),
                       format_func=lambda x: event_map[x])

    # Get current event details
    ev = next((e for e in events if e["id"] == eid), None)
    if not ev:
        st.error("Event not found.")
        return

    with st.form("update_event"):
        n_name = st.text_input("Name", ev["name"])
        n_desc = st.text_area("Description", ev.get("description", ""))
        n_date = st.date_input("Date", ev["date"])

        # Parse time strings from API
        def parse_time(t):
            if isinstance(t, str):
                parts = t.split(":")
                return datetime.time(int(parts[0]), int(parts[1]))
            return t

        n_start = st.time_input("Start", parse_time(ev["start_time"]))
        n_end = st.time_input("End", parse_time(ev["end_time"]))

        if st.form_submit_button("Update"):
            try:
                update_event(eid, name=n_name, description=n_desc,
                             date=n_date, start_time=n_start, end_time=n_end)
                st.success("Updated.")
            except requests.HTTPError as e:
                st.error(f"Failed: {e.response.text}")


def display_manage_event_tickets():
    st.subheader("Manage Tickets")

    try:
        events = get_all_events()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not events:
        st.info("No events found.")
        return

    event_map = {e["id"]: e["name"] for e in events}
    eid = st.selectbox("Event", list(event_map.keys()),
                       format_func=lambda x: event_map[x])

    try:
        tickets = get_tickets(eid)
    except requests.RequestException:
        tickets = []

    if tickets:
        df = pd.DataFrame(tickets)
        df = df[["id", "ticket_type", "price", "quantity"]]
        df.columns = ["ID", "Type", "Price", "Qty"]
        st.dataframe(df, hide_index=True)

    with st.form("add_ticket"):
        ttype = st.text_input("Ticket Type")
        price = st.number_input("Price", 0.0)
        qty = st.number_input("Quantity", 0)
        if st.form_submit_button("Add"):
            try:
                create_ticket(eid, ttype, price, qty)
                st.success("Ticket added.")
            except requests.HTTPError as e:
                st.error(f"Failed: {e.response.text}")


def display_mark_attendance():
    st.subheader("Mark Attendance")

    try:
        events = get_all_events()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not events:
        st.info("No events found.")
        return

    event_map = {e["id"]: e["name"] for e in events}
    eid = st.selectbox("Event", list(event_map.keys()),
                       format_func=lambda x: event_map[x])

    try:
        parts = get_participants(eid)
    except requests.RequestException:
        parts = []

    if not parts:
        st.info("No participants.")
        return

    df = pd.DataFrame(parts)
    df.columns = ["ID", "Name", "SRN", "Attended"]
    st.dataframe(df, hide_index=True)

    sid = st.selectbox("Student ID", [p["student_id"] for p in parts])
    if st.button("Mark Attended"):
        try:
            mark_attendance(eid, sid)
            st.success("Marked attended.")
        except requests.HTTPError as e:
            st.error(f"Failed: {e.response.text}")


def display_view_participants():
    st.subheader("Participants")

    try:
        rows = get_all_participants()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if rows:
        df = pd.DataFrame(rows)
        df.columns = ["Event", "Student", "SRN", "Attended"]
        st.dataframe(df, hide_index=True)
    else:
        st.info("No data.")


def display_view_users():
    st.subheader("Users")

    try:
        from services.api_client import get_students
        students = get_students()
        hosts = get_hosts()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    st.markdown("### Students")
    if students:
        df = pd.DataFrame(students)
        df = df[["id", "srn", "name", "semester", "section"]]
        df.columns = ["ID", "SRN", "Name", "Sem", "Sec"]
        st.dataframe(df, hide_index=True)

    st.markdown("### Hosts")
    if hosts:
        df = pd.DataFrame(hosts)
        df.columns = ["ID", "Name", "Dept", "Role"]
        st.dataframe(df, hide_index=True)


def display_manage_venues():
    st.subheader("Venues")

    try:
        venues = get_venues()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    df = pd.DataFrame(venues)
    df = df[["id", "name", "building", "capacity", "is_available"]]
    df.columns = ["ID", "Name", "Building", "Capacity", "Available"]
    st.dataframe(df, hide_index=True)

    vid = st.selectbox("Venue ID", [v["id"] for v in venues])
    status = st.radio("Availability", [1, 0])
    status_bool = True if status == 1 else False

    if st.button("Update"):
        try:
            update_venue(vid, status_bool)
            st.success("Updated.")
        except requests.HTTPError as e:
            st.error(f"Failed: {e.response.text}")


def display_manage_resources():
    st.subheader("Resource Management")

    try:
        resources = get_resources()
    except requests.RequestException as e:
        st.error(f"Service error: {e}")
        return

    if not resources:
        st.info("No resources.")
        return

    df = pd.DataFrame(resources)
    df = df[["id", "name", "type", "quantity", "maintenance_status"]]
    df.columns = ["ID", "Name", "Type", "Quantity", "Status"]
    st.dataframe(df, hide_index=True)

    st.markdown("---")
    st.markdown("### Assign Resource to Event")

    try:
        events = get_scheduled_events()
    except requests.RequestException:
        events = []

    if not events:
        st.info("No upcoming events.")
        return

    event_map = {e["id"]: e["name"] for e in events}
    resource_map = {r["id"]: f"{r['name']} ({r['quantity']} available)" for r in resources}

    event_id = st.selectbox("Select Event", list(event_map.keys()),
                            format_func=lambda x: event_map[x])
    resource_id = st.selectbox("Select Resource", list(resource_map.keys()),
                               format_func=lambda x: resource_map[x])
    qty = st.number_input("Quantity to Assign", min_value=1, value=1)

    col1, col2 = st.columns(2)
    start_date = col1.date_input("Booking Start Date", key="book_start_date")
    start_time = col1.time_input("Booking Start Time", datetime.time(9, 0),
                                 key="book_start_time")
    end_date = col2.date_input("Booking End Date", key="book_end_date")
    end_time = col2.time_input("Booking End Time", datetime.time(17, 0),
                               key="book_end_time")

    if st.button("Assign Resource"):
        start_dt = datetime.datetime.combine(start_date, start_time)
        end_dt = datetime.datetime.combine(end_date, end_time)
        if end_dt <= start_dt:
            st.error("Booking end must be after start.")
            return

        try:
            assign_resource(event_id, resource_id, qty, start_dt, end_dt)
            st.success("Resource assigned.")
        except requests.HTTPError as e:
            st.error(f"Failed: {e.response.text}")

    st.markdown("---")
    st.markdown("### Replenish Expired Resource Bookings")

    if st.button("Run Replenish Resources"):
        try:
            result = replenish_resources()
            restored = result.get("restored", 0)
            if restored > 0:
                st.success(f"Resources replenished: {restored}")
            else:
                st.info("No resources needed replenishment.")
        except requests.HTTPError as e:
            st.error(f"Failed: {e.response.text}")

    st.markdown("---")
    st.markdown("### Schedule Resource Maintenance")

    res_map = {r["id"]: r["name"] for r in resources}
    res_id = st.selectbox("Resource", list(res_map.keys()),
                          format_func=lambda x: res_map[x])

    col1, col2 = st.columns(2)
    m_start_date = col1.date_input("Maintenance Start Date", key="maint_start_date")
    m_start_time = col1.time_input("Maintenance Start Time", datetime.time(9, 0),
                                   key="maint_start_time")
    m_end_date = col2.date_input("Maintenance End Date", key="maint_end_date")
    m_end_time = col2.time_input("Maintenance End Time", datetime.time(17, 0),
                                 key="maint_end_time")

    reason = st.text_input("Reason")

    if st.button("Start Maintenance"):
        m_start = datetime.datetime.combine(m_start_date, m_start_time)
        m_end = datetime.datetime.combine(m_end_date, m_end_time)
        if m_end <= m_start:
            st.error("Maintenance end must be after start.")
            return

        try:
            schedule_maintenance(res_id, m_start, m_end, reason)
            st.success("Resource sent to maintenance.")
        except requests.HTTPError as e:
            st.error(f"Failed: {e.response.text}")
