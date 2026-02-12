from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime


# ──────────── Events ────────────

class EventOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    date: date
    start_time: time
    end_time: time
    location_id: Optional[int] = None
    venue_name: Optional[str] = None
    organizer_id: Optional[int] = None
    host_name: Optional[str] = None
    status: Optional[str] = None
    max_participants: Optional[int] = None


class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    date: date
    start_time: time
    end_time: time
    location_id: int
    organizer_id: int
    max_participants: int = 50


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


# ──────────── Venues ────────────

class VenueOut(BaseModel):
    id: int
    name: str
    building: Optional[str] = None
    capacity: Optional[int] = None
    is_available: Optional[bool] = None


class VenueUpdate(BaseModel):
    is_available: bool


# ──────────── Tickets ────────────

class TicketOut(BaseModel):
    id: int
    event_id: int
    ticket_type: str
    price: float
    quantity: int


class TicketCreate(BaseModel):
    ticket_type: str
    price: float
    quantity: int


# ──────────── Registration ────────────

class RegisterRequest(BaseModel):
    user_id: int
    ticket_id: int


class CancelRequest(BaseModel):
    user_id: int


# ──────────── Orders ────────────

class OrderOut(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    order_time: Optional[datetime] = None
    payment_status: Optional[str] = None


# ──────────── Participants ────────────

class ParticipantOut(BaseModel):
    student_id: int
    student_name: str
    srn: str
    attendance_status: Optional[bool] = None


class RegistrationOut(BaseModel):
    event_id: int
    event_name: str
    date: date
    start_time: time
    venue_name: Optional[str] = None


# ──────────── Resources ────────────

class ResourceOut(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    quantity: int
    maintenance_status: Optional[str] = None


class ResourceAssign(BaseModel):
    resource_id: int
    quantity_booked: int
    booking_start: datetime
    booking_end: datetime


class MaintenanceCreate(BaseModel):
    maintenance_start: datetime
    maintenance_end: datetime
    description: Optional[str] = None
