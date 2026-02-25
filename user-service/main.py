from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from database import get_cursor
from models import StudentOut, StudentCreate, HostOut
import asyncio
import httpx
import os

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


app = FastAPI(title="Eventra User Service", version="1.0.0", lifespan=lifespan)


# ──────────── Health ────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "user-service"}


# ──────────── Students ────────────

@app.get("/students", response_model=list[StudentOut])
def list_students():
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, srn, name, semester, section FROM tbl_students ORDER BY name"
        )
        return cur.fetchall()


@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, srn, name, semester, section FROM tbl_students WHERE id=%s",
            (student_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        return row


@app.post("/students", response_model=StudentOut, status_code=201)
def create_student(student: StudentCreate):
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO tbl_students (srn, name, semester, section)
            VALUES (%s, %s, %s, %s)
            RETURNING id, srn, name, semester, section
            """,
            (student.srn, student.name, student.semester, student.section),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create student")
        return row


# ──────────── Hosts ────────────

@app.get("/hosts", response_model=list[HostOut])
def list_hosts():
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, department, role FROM tbl_hosts ORDER BY name"
        )
        return cur.fetchall()
