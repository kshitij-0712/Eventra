from pydantic import BaseModel
from typing import Optional


class StudentOut(BaseModel):
    id: int
    srn: str
    name: str
    semester: int
    section: str


class StudentCreate(BaseModel):
    srn: str
    name: str
    semester: int
    section: str


class HostOut(BaseModel):
    id: int
    name: str
    department: Optional[str] = None
    role: Optional[str] = None
