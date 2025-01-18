# backend/schemas/attendance.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AttendanceBase(BaseModel):
    user_id: int
    materia: str
    fecha: datetime
    confidence: float
    status: str

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int

    class Config:
        from_attributes = True 