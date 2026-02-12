"""
API Client — HTTP wrapper for Eventra microservices.
The Streamlit frontend calls these functions instead of the database directly.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://localhost:8002")
FEEDBACK_SERVICE_URL = os.getenv("FEEDBACK_SERVICE_URL", "http://localhost:8003")

TIMEOUT = 10  # seconds


# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════

def _get(url, **kwargs):
    resp = requests.get(url, timeout=TIMEOUT, **kwargs)
    resp.raise_for_status()
    return resp.json()


def _post(url, json=None, **kwargs):
    resp = requests.post(url, json=json, timeout=TIMEOUT, **kwargs)
    resp.raise_for_status()
    return resp.json()


def _put(url, json=None, **kwargs):
    resp = requests.put(url, json=json, timeout=TIMEOUT, **kwargs)
    resp.raise_for_status()
    return resp.json()


def _delete(url, **kwargs):
    resp = requests.delete(url, timeout=TIMEOUT, **kwargs)
    resp.raise_for_status()
    return resp.json()


# ══════════════════════════════════════════
#  USER SERVICE
# ══════════════════════════════════════════

def get_students():
    return _get(f"{USER_SERVICE_URL}/students")


def get_student(student_id):
    return _get(f"{USER_SERVICE_URL}/students/{student_id}")


def create_student(srn, name, semester, section):
    return _post(f"{USER_SERVICE_URL}/students", json={
        "srn": srn, "name": name, "semester": semester, "section": section,
    })


def get_hosts():
    return _get(f"{USER_SERVICE_URL}/hosts")


# ══════════════════════════════════════════
#  EVENT SERVICE — Events
# ══════════════════════════════════════════

def get_scheduled_events():
    return _get(f"{EVENT_SERVICE_URL}/events")


def get_completed_events():
    return _get(f"{EVENT_SERVICE_URL}/events/completed")


def get_all_events():
    return _get(f"{EVENT_SERVICE_URL}/events/all")


def get_event(event_id):
    return _get(f"{EVENT_SERVICE_URL}/events/{event_id}")


def create_event(name, description, date, start_time, end_time,
                 location_id, organizer_id, max_participants):
    return _post(f"{EVENT_SERVICE_URL}/events", json={
        "name": name,
        "description": description,
        "date": str(date),
        "start_time": str(start_time),
        "end_time": str(end_time),
        "location_id": location_id,
        "organizer_id": organizer_id,
        "max_participants": max_participants,
    })


def update_event(event_id, **fields):
    # Convert date/time objects to strings for JSON
    payload = {}
    for k, v in fields.items():
        if v is not None:
            payload[k] = str(v) if hasattr(v, 'isoformat') else v
    return _put(f"{EVENT_SERVICE_URL}/events/{event_id}", json=payload)


# ══════════════════════════════════════════
#  EVENT SERVICE — Venues
# ══════════════════════════════════════════

def get_venues():
    return _get(f"{EVENT_SERVICE_URL}/venues")


def get_available_venues():
    return _get(f"{EVENT_SERVICE_URL}/venues/available")


def update_venue(venue_id, is_available):
    return _put(f"{EVENT_SERVICE_URL}/venues/{venue_id}", json={
        "is_available": is_available,
    })


# ══════════════════════════════════════════
#  EVENT SERVICE — Tickets
# ══════════════════════════════════════════

def get_tickets(event_id):
    return _get(f"{EVENT_SERVICE_URL}/events/{event_id}/tickets")


def create_ticket(event_id, ticket_type, price, quantity):
    return _post(f"{EVENT_SERVICE_URL}/events/{event_id}/tickets", json={
        "ticket_type": ticket_type, "price": price, "quantity": quantity,
    })


# ══════════════════════════════════════════
#  EVENT SERVICE — Registration
# ══════════════════════════════════════════

def register_for_event(event_id, user_id, ticket_id):
    return _post(f"{EVENT_SERVICE_URL}/events/{event_id}/register", json={
        "user_id": user_id, "ticket_id": ticket_id,
    })


def cancel_registration(event_id, user_id):
    return _delete(f"{EVENT_SERVICE_URL}/events/{event_id}/register/{user_id}")


# ══════════════════════════════════════════
#  EVENT SERVICE — Participants & Attendance
# ══════════════════════════════════════════

def get_participants(event_id):
    return _get(f"{EVENT_SERVICE_URL}/events/{event_id}/participants")


def get_all_participants():
    return _get(f"{EVENT_SERVICE_URL}/participants/all")


def mark_attendance(event_id, user_id):
    return _put(f"{EVENT_SERVICE_URL}/events/{event_id}/attendance/{user_id}")


def get_user_registrations(user_id):
    return _get(f"{EVENT_SERVICE_URL}/registrations/{user_id}")


# ══════════════════════════════════════════
#  EVENT SERVICE — Resources
# ══════════════════════════════════════════

def get_resources():
    return _get(f"{EVENT_SERVICE_URL}/resources")


def assign_resource(event_id, resource_id, quantity_booked,
                    booking_start, booking_end):
    return _post(f"{EVENT_SERVICE_URL}/events/{event_id}/resources", json={
        "resource_id": resource_id,
        "quantity_booked": quantity_booked,
        "booking_start": str(booking_start),
        "booking_end": str(booking_end),
    })


def replenish_resources():
    return _post(f"{EVENT_SERVICE_URL}/resources/replenish")


def schedule_maintenance(resource_id, maintenance_start,
                         maintenance_end, description):
    return _post(f"{EVENT_SERVICE_URL}/resources/{resource_id}/maintenance", json={
        "maintenance_start": str(maintenance_start),
        "maintenance_end": str(maintenance_end),
        "description": description,
    })


# ══════════════════════════════════════════
#  FEEDBACK SERVICE
# ══════════════════════════════════════════

def get_feedback(event_id):
    return _get(f"{FEEDBACK_SERVICE_URL}/feedback/{event_id}")


def get_average_rating(event_id):
    return _get(f"{FEEDBACK_SERVICE_URL}/feedback/{event_id}/average")


def submit_feedback(event_id, user_id, rating, comments):
    return _post(f"{FEEDBACK_SERVICE_URL}/feedback", json={
        "event_id": event_id,
        "user_id": user_id,
        "rating": rating,
        "comments": comments,
    })
