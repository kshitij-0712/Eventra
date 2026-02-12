from fastapi import FastAPI, HTTPException
from database import get_cursor
from models import FeedbackOut, FeedbackCreate, AverageRatingOut
import datetime

app = FastAPI(title="Eventra Feedback Service", version="1.0.0")


# ──────────── Health ────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "feedback-service"}


# ──────────── Feedback ────────────

@app.get("/feedback/{event_id}", response_model=list[FeedbackOut])
def list_feedback(event_id: int):
    """List all feedback for an event, with student names."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT f.id, f.event_id, f.user_id,
                   s.name AS student_name, s.srn,
                   f.rating, f.comments, f.submitted_at
            FROM tbl_event_feedback f
            LEFT JOIN tbl_students s ON f.user_id = s.id
            WHERE f.event_id = %s
            ORDER BY f.submitted_at DESC
        """, (event_id,))
        return cur.fetchall()


@app.get("/feedback/{event_id}/average", response_model=AverageRatingOut)
def get_average_rating(event_id: int):
    """Compute average rating for an event."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT COALESCE(AVG(rating), 0) AS avg_rating,
                   COUNT(*) AS total
            FROM tbl_event_feedback
            WHERE event_id = %s
        """, (event_id,))
        row = cur.fetchone()
        return AverageRatingOut(
            event_id=event_id,
            average_rating=round(float(row["avg_rating"]), 2),
            total_reviews=int(row["total"]),
        )


@app.post("/feedback", status_code=201)
def submit_feedback(req: FeedbackCreate):
    """
    Submit feedback for an event.
    Checks:
    1. Student attended the event (attendance_status = TRUE)
    2. Student hasn't already submitted feedback
    """
    with get_cursor(commit=True) as cur:
        # Check attendance
        cur.execute("""
            SELECT attendance_status
            FROM tbl_event_participants
            WHERE event_id = %s AND user_id = %s
        """, (req.event_id, req.user_id))
        part = cur.fetchone()

        if not part or part["attendance_status"] is not True:
            raise HTTPException(
                status_code=403,
                detail="Attendance not marked for this event",
            )

        # Check for duplicate feedback
        cur.execute("""
            SELECT id FROM tbl_event_feedback
            WHERE event_id = %s AND user_id = %s
        """, (req.event_id, req.user_id))
        if cur.fetchone():
            raise HTTPException(
                status_code=409,
                detail="Feedback already submitted for this event",
            )

        # Validate rating range
        if req.rating < 1 or req.rating > 5:
            raise HTTPException(
                status_code=400, detail="Rating must be between 1 and 5"
            )

        # Insert feedback
        now = datetime.datetime.now()
        cur.execute("""
            INSERT INTO tbl_event_feedback
            (event_id, user_id, rating, comments, submitted_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (req.event_id, req.user_id, req.rating, req.comments, now))

        row = cur.fetchone()
        if not row:
            raise HTTPException(
                status_code=500, detail="Failed to submit feedback"
            )

        return {"message": "Feedback submitted", "feedback_id": row["id"]}
