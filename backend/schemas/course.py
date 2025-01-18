# backend/schemas/course.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import time

class CourseBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    horas: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    horas: Optional[int] = None

class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True