# backend/services/attendance_manager.py
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from models.attendance import Attendance
from models.user import User
import logging

class AttendanceManager:
    def __init__(self, db: Session):
        self.db = db

    def register_attendance(
        self, 
        user_id: int, 
        materia: str, 
        confidence: float
    ) -> bool:
        try:
            attendance = Attendance(
                user_id=user_id,
                materia=materia,
                fecha=datetime.utcnow(),
                confidence=confidence,
                status="PRESENTE"
            )
            self.db.add(attendance)
            self.db.commit()
            return True
        except Exception as e:
            logging.error(f"Error al registrar asistencia: {str(e)}")
            self.db.rollback()
            return False

    def get_attendance_report(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        materia: str = None
    ) -> List[Dict]:
        query = self.db.query(
            Attendance
        ).join(
            User
        ).filter(
            Attendance.fecha.between(fecha_inicio, fecha_fin)
        )

        if materia:
            query = query.filter(Attendance.materia == materia)

        return query.all()