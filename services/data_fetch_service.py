from utils.helpers import execute_query


def list_all_students(cursor=None):
    """Fetches all students."""
    if cursor is None:
        students = execute_query(
            "SELECT id, srn, name, semester, section FROM tbl_students ORDER BY name"
        )
        return students
    return execute_query(
        "SELECT id, srn, name, semester, section FROM tbl_students ORDER BY name",
        cursor=cursor
    )


def list_all_hosts():
    """Fetches all hosts."""
    return execute_query(
        "SELECT id, name, department, role FROM tbl_hosts ORDER BY name"
    )


def list_all_venues():
    """Fetches all venues."""
    return execute_query(
        "SELECT id, name, building, capacity, is_available FROM tbl_venues ORDER BY name"
    )


def list_available_venues():
    """Fetches only available venues."""
    return execute_query(
        "SELECT id, name, building, capacity FROM tbl_venues WHERE is_available = 1 ORDER BY capacity DESC"
    )


def list_scheduled_events():
    """Fetches upcoming events for display."""
    query = """
        SELECT
            e.id,
            e.name,
            e.description,
            e.date,
            e.start_time,
            e.end_time,
            v.name AS venue_name,
            h.name AS host_name,
            e.location_id
        FROM tbl_events e
        LEFT JOIN tbl_venues v ON e.location_id = v.id
        JOIN tbl_hosts h ON e.organizer_id = h.id
        WHERE CONCAT(e.date, ' ', e.end_time) > NOW()
        ORDER BY e.date, e.start_time
    """
    return execute_query(query)


def list_all_resources():
    """Fetches all resources."""
    return execute_query(
        "SELECT id, name, type, quantity, maintenance_status FROM tbl_resources ORDER BY name"
    )
