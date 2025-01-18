# backend/models/attendance.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
from datetime import datetime

class Attendance(Base, TimestampMixin):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    materia = Column(String(100), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    confidence = Column(Float, CheckConstraint('confidence >= 0 AND confidence <= 1'))
    status = Column(String(20), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="attendances")

    __table_args__ = (
        CheckConstraint("status IN ('PRESENTE', 'AUSENTE')", name='valid_status'),
    )

    def __repr__(self):
        return f"<Attendance {self.user_id} - {self.fecha}>"