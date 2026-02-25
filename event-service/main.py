from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from database import get_cursor
from models import (
    EventOut, EventCreate, EventUpdate,
    VenueOut, VenueUpdate,
    TicketOut, TicketCreate,
    RegisterRequest,
    ParticipantOut, RegistrationOut,
    ResourceOut, ResourceAssign, MaintenanceCreate,
)
import datetime
import asyncio
import httpx

# URLs of all services to keep alive
KEEP_ALIVE_URLS = [
    "https://eventra-xgrj.onrender.com/health",           # user-service
    "https://eventra-event-service.onrender.com/health",  # event-service
    "https://eventra-feedbacke-service.onrender.com/health",  # feedback-service
    "https://eventra-cc.streamlit.app/",                  # frontend
]

PING_INTERVAL = 600  # 10 minutes


async def keep_alive_task():
    """Background task that pings all services every 10 minutes."""
    while True:
        await asyncio.sleep(PING_INTERVAL)
        async with httpx.AsyncClient(timeout=30) as client:
            for url in KEEP_ALIVE_URLS:
                try:
                    resp = await client.get(url)
                    print(f"[keep-alive] Pinged {url} -> {resp.status_code}")
                except Exception as e:
                    print(f"[keep-alive] Failed to ping {url}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start keep-alive background task on startup."""
    task = asyncio.create_task(keep_alive_task())
    print("[keep-alive] Background ping task started")
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("[keep-alive] Background task stopped")


app = FastAPI(title="Eventra Event Service", version="1.0.0", lifespan=lifespan)


# ──────────── Health ────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "event-service"}


# ══════════════════════════════════════════
#  EVENTS
# ══════════════════════════════════════════

@app.get("/events", response_model=list[EventOut])
def list_scheduled_events():
    """List events that haven't ended yet (scheduled/upcoming)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT e.id, e.name, e.description, e.date,
                   e.start_time, e.end_time,
                   e.location_id, v.name AS venue_name,
                   e.organizer_id, h.name AS host_name,
                   e.status, e.max_participants
            FROM tbl_events e
            LEFT JOIN tbl_venues v ON e.location_id = v.id
            LEFT JOIN tbl_hosts h ON e.organizer_id = h.id
            WHERE (e.date + e.end_time) > NOW()
            ORDER BY e.date, e.start_time
        """)
        return cur.fetchall()


@app.get("/events/completed", response_model=list[EventOut])
def list_completed_events():
    """List events that have already ended."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT e.id, e.name, e.description, e.date,
                   e.start_time, e.end_time,
                   e.location_id, v.name AS venue_name,
                   e.organizer_id, h.name AS host_name,
                   e.status, e.max_participants
            FROM tbl_events e
            LEFT JOIN tbl_venues v ON e.location_id = v.id
            LEFT JOIN tbl_hosts h ON e.organizer_id = h.id
            WHERE (e.date + e.end_time) <= NOW()
            ORDER BY e.date DESC
        """)
        return cur.fetchall()


@app.get("/events/all", response_model=list[EventOut])
def list_all_events():
    """List all events (for admin views like ticket management)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT e.id, e.name, e.description, e.date,
                   e.start_time, e.end_time,
                   e.location_id, v.name AS venue_name,
                   e.organizer_id, h.name AS host_name,
                   e.status, e.max_participants
            FROM tbl_events e
            LEFT JOIN tbl_venues v ON e.location_id = v.id
            LEFT JOIN tbl_hosts h ON e.organizer_id = h.id
            ORDER BY e.date DESC
        """)
        return cur.fetchall()


@app.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int):
    with get_cursor() as cur:
        cur.execute("""
            SELECT e.id, e.name, e.description, e.date,
                   e.start_time, e.end_time,
                   e.location_id, v.name AS venue_name,
                   e.organizer_id, h.name AS host_name,
                   e.status, e.max_participants
            FROM tbl_events e
            LEFT JOIN tbl_venues v ON e.location_id = v.id
            LEFT JOIN tbl_hosts h ON e.organizer_id = h.id
            WHERE e.id = %s
        """, (event_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Event not found")
        return row


@app.post("/events", response_model=EventOut, status_code=201)
def create_event(event: EventCreate):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO tbl_events
            (name, description, date, start_time, end_time,
             location_id, organizer_id, status, max_participants)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Scheduled', %s)
            RETURNING id, name, description, date, start_time, end_time,
                      location_id, organizer_id, status, max_participants
        """, (
            event.name, event.description, event.date,
            event.start_time, event.end_time,
            event.location_id, event.organizer_id,
            event.max_participants,
        ))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create event")
        return row


@app.put("/events/{event_id}")
def update_event(event_id: int, event: EventUpdate):
    fields = []
    values = []
    for field_name, value in event.model_dump(exclude_none=True).items():
        fields.append(f"{field_name} = %s")
        values.append(value)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(event_id)

    with get_cursor(commit=True) as cur:
        cur.execute(
            f"UPDATE tbl_events SET {', '.join(fields)} WHERE id = %s",
            tuple(values),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"message": "Event updated"}


# ══════════════════════════════════════════
#  VENUES
# ══════════════════════════════════════════

@app.get("/venues", response_model=list[VenueOut])
def list_venues():
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, building, capacity, is_available "
            "FROM tbl_venues ORDER BY name"
        )
        return cur.fetchall()


@app.get("/venues/available", response_model=list[VenueOut])
def list_available_venues():
    with get_cursor() as cur:
        cur.execute("""
            SELECT id, name, building, capacity, is_available
            FROM tbl_venues
            WHERE is_available = TRUE
            ORDER BY capacity DESC
        """)
        return cur.fetchall()


@app.put("/venues/{venue_id}")
def update_venue(venue_id: int, venue: VenueUpdate):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE tbl_venues SET is_available = %s WHERE id = %s",
            (venue.is_available, venue_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Venue not found")
        return {"message": "Venue updated"}


# ══════════════════════════════════════════
#  TICKETS
# ══════════════════════════════════════════

@app.get("/events/{event_id}/tickets", response_model=list[TicketOut])
def list_tickets(event_id: int):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, event_id, ticket_type, price, quantity "
            "FROM tbl_tickets WHERE event_id = %s",
            (event_id,),
        )
        return cur.fetchall()


@app.post("/events/{event_id}/tickets", status_code=201)
def create_ticket(event_id: int, ticket: TicketCreate):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO tbl_tickets (event_id, ticket_type, price, quantity)
            VALUES (%s, %s, %s, %s)
            RETURNING id, event_id, ticket_type, price, quantity
        """, (event_id, ticket.ticket_type, ticket.price, ticket.quantity))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create ticket")
        return row


# ══════════════════════════════════════════
#  REGISTRATION (transactional)
# ══════════════════════════════════════════

@app.post("/events/{event_id}/register", status_code=201)
def register_for_event(event_id: int, req: RegisterRequest):
    """
    Atomic registration: check duplicate -> lock ticket row ->
    decrement quantity -> insert order -> insert participant.
    All in a single transaction with SELECT FOR UPDATE.
    """
    with get_cursor(commit=True) as cur:
        # 1. Check if already registered
        cur.execute(
            "SELECT 1 FROM tbl_event_participants "
            "WHERE event_id = %s AND user_id = %s",
            (event_id, req.user_id),
        )
        if cur.fetchone():
            raise HTTPException(
                status_code=409,
                detail="Already registered for this event",
            )

        # 2. Lock the ticket row and check availability
        cur.execute(
            "SELECT quantity FROM tbl_tickets WHERE id = %s FOR UPDATE",
            (req.ticket_id,),
        )
        ticket = cur.fetchone()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if ticket["quantity"] < 1:
            raise HTTPException(
                status_code=400, detail="Tickets sold out"
            )

        # 3. Decrement ticket quantity
        cur.execute(
            "UPDATE tbl_tickets SET quantity = quantity - 1 WHERE id = %s",
            (req.ticket_id,),
        )

        # 4. Create order
        now = datetime.datetime.now()
        cur.execute("""
            INSERT INTO tbl_orders (ticket_id, user_id, order_time, payment_status)
            VALUES (%s, %s, %s, 'Completed')
        """, (req.ticket_id, req.user_id, now))

        # 5. Create participant record
        cur.execute("""
            INSERT INTO tbl_event_participants (event_id, user_id, registration_time)
            VALUES (%s, %s, %s)
        """, (event_id, req.user_id, now))

    return {"message": "Successfully registered"}


@app.delete("/events/{event_id}/register/{user_id}")
def cancel_registration(event_id: int, user_id: int):
    """
    Atomic cancellation: lock ticket rows -> find order ->
    restock ticket -> delete order -> delete participant.
    All in a single transaction.
    """
    with get_cursor(commit=True) as cur:
        # 1. Lock all ticket rows for this event (prevent concurrent mods)
        cur.execute(
            "SELECT id FROM tbl_tickets WHERE event_id = %s FOR UPDATE",
            (event_id,),
        )

        # 2. Find the student's order for this event
        cur.execute("""
            SELECT o.ticket_id
            FROM tbl_orders o
            JOIN tbl_tickets t ON o.ticket_id = t.id
            WHERE o.user_id = %s AND t.event_id = %s
        """, (user_id, event_id))
        order_row = cur.fetchone()

        if order_row:
            # 3. Restock the ticket (+1)
            cur.execute(
                "UPDATE tbl_tickets SET quantity = quantity + 1 WHERE id = %s",
                (order_row["ticket_id"],),
            )

            # 4. Delete the order
            cur.execute("""
                DELETE FROM tbl_orders
                WHERE user_id = %s
                  AND ticket_id IN (
                      SELECT id FROM tbl_tickets WHERE event_id = %s
                  )
            """, (user_id, event_id))

        # 5. Delete participant record
        cur.execute(
            "DELETE FROM tbl_event_participants "
            "WHERE event_id = %s AND user_id = %s",
            (event_id, user_id),
        )

        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Registration not found"
            )

    return {"message": "Registration cancelled successfully"}


# ══════════════════════════════════════════
#  PARTICIPANTS & ATTENDANCE
# ══════════════════════════════════════════

@app.get("/events/{event_id}/participants", response_model=list[ParticipantOut])
def list_participants(event_id: int):
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.id AS student_id, s.name AS student_name,
                   s.srn, p.attendance_status
            FROM tbl_event_participants p
            JOIN tbl_students s ON p.user_id = s.id
            WHERE p.event_id = %s
        """, (event_id,))
        return cur.fetchall()


@app.get("/participants/all")
def list_all_participants():
    """All participants across all events (admin view)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT e.name AS event_name, s.name AS student_name,
                   s.srn, p.attendance_status
            FROM tbl_event_participants p
            JOIN tbl_events e ON p.event_id = e.id
            JOIN tbl_students s ON p.user_id = s.id
        """)
        return cur.fetchall()


@app.put("/events/{event_id}/attendance/{user_id}")
def mark_attendance(event_id: int, user_id: int):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE tbl_event_participants "
            "SET attendance_status = TRUE "
            "WHERE event_id = %s AND user_id = %s",
            (event_id, user_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Participant not found"
            )
        return {"message": "Attendance marked"}


@app.get("/registrations/{user_id}", response_model=list[RegistrationOut])
def list_user_registrations(user_id: int):
    """Get upcoming registrations for a specific student."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT e.id AS event_id, e.name AS event_name,
                   e.date, e.start_time,
                   v.name AS venue_name
            FROM tbl_event_participants p
            JOIN tbl_events e ON p.event_id = e.id
            LEFT JOIN tbl_venues v ON e.location_id = v.id
            WHERE p.user_id = %s
              AND (e.date + e.end_time) > NOW()
            ORDER BY e.date
        """, (user_id,))
        return cur.fetchall()


# ══════════════════════════════════════════
#  RESOURCES
# ══════════════════════════════════════════

@app.get("/resources", response_model=list[ResourceOut])
def list_resources():
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, type, quantity, maintenance_status "
            "FROM tbl_resources ORDER BY name"
        )
        return cur.fetchall()


@app.post("/events/{event_id}/resources", status_code=201)
def assign_resource(event_id: int, req: ResourceAssign):
    if req.booking_end <= req.booking_start:
        raise HTTPException(
            status_code=400, detail="Booking end must be after start"
        )

    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO tbl_event_resources
            (event_id, resource_id, quantity_booked, booking_start, booking_end)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            event_id, req.resource_id, req.quantity_booked,
            req.booking_start, req.booking_end,
        ))
        return {"message": "Resource assigned"}


@app.post("/resources/replenish")
def replenish_resources():
    with get_cursor(commit=True) as cur:
        cur.execute("SELECT replenish_resources()")
        row = cur.fetchone()
        restored = row["replenish_resources"] if row else 0
        return {"restored": restored}


@app.post("/resources/{resource_id}/maintenance", status_code=201)
def schedule_maintenance(resource_id: int, req: MaintenanceCreate):
    if req.maintenance_end <= req.maintenance_start:
        raise HTTPException(
            status_code=400,
            detail="Maintenance end must be after start",
        )

    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO tbl_resource_maintenance
            (resource_id, maintenance_start, maintenance_end, description)
            VALUES (%s, %s, %s, %s)
        """, (
            resource_id, req.maintenance_start,
            req.maintenance_end, req.description,
        ))
        return {"message": "Maintenance scheduled"}
