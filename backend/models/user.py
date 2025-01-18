# backend/models/user.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    rol = Column(Enum(UserRole), nullable=False)
    horario = Column(String(100))
    facultad = Column(String(100))
    universidad = Column(String(100))
    materia_id = Column(Integer, ForeignKey('courses.id'))

    # Relaciones
    attendances = relationship("Attendance", back_populates="user")
    course = relationship("Course", back_populates="users")

    def __repr__(self):
        return f"<User {self.nombre} {self.apellido}>"