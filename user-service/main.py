from fastapi import FastAPI, HTTPException
from database import get_cursor
from models import StudentOut, StudentCreate, HostOut

app = FastAPI(title="Eventra User Service", version="1.0.0")


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
