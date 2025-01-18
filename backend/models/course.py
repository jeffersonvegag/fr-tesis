# backend/models/course.py
from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(200))
    horas = Column(Integer, nullable=False)

    # Relaciones
    schedules = relationship("Schedule", back_populates="course")
    users = relationship("User", back_populates="course")

    def __repr__(self):
        return f"<Course {self.nombre}>"

class Schedule(Base, TimestampMixin):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    # Relación
    course = relationship("Course", back_populates="schedules")

    def __repr__(self):
        return f"<Schedule {self.hora_inicio} - {self.hora_fin}>"