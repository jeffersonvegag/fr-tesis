# backend/api/endpoints/attendance.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from core.database import get_db
from models.attendance import Attendance
from models.user import User
from schemas.attendance import AttendanceCreate, AttendanceResponse
import pandas as pd
from fastapi.responses import FileResponse
import os
# En todos los archivos de endpoints
from db.session import get_db  # Actualizar esta importación

router = APIRouter()

@router.post("/attendance/", response_model=AttendanceResponse)
async def create_attendance(
    attendance: AttendanceCreate, 
    db: Session = Depends(get_db)
):
    db_attendance = Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.get("/attendance/", response_model=List[AttendanceResponse])
async def get_attendance(
    fecha_inicio: date = Query(None),
    fecha_fin: date = Query(None),
    materia: str = Query(None),
    docente: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Attendance).join(User)
    
    if fecha_inicio:
        query = query.filter(Attendance.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Attendance.fecha <= fecha_fin)
    if materia:
        query = query.filter(Attendance.materia == materia)
    if docente:
        query = query.filter(User.nombre.contains(docente))
    
    return query.all()

@router.get("/attendance/download")
async def download_attendance_report(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    materia: str = Query(None),
    formato: str = Query(..., regex="^(csv|xlsx)$"),
    db: Session = Depends(get_db)
):
    # Obtener datos de asistencia
    query = db.query(
        Attendance, 
        User
    ).join(User)
    
    if materia:
        query = query.filter(Attendance.materia == materia)
    
    query = query.filter(
        Attendance.fecha.between(fecha_inicio, fecha_fin)
    )
    
    results = query.all()
    
    # Crear DataFrame
    data = []
    for attendance, user in results:
        data.append({
            "ID": user.id,
            "ASISTENCIA": "SI" if attendance.status == "PRESENTE" else "NO",
            "CEDULA": user.cedula,
            "NOMBRE": user.nombre,
            "APELLIDO": user.apellido,
            "MATERIA": attendance.materia,
            "CURSO": user.horario,
            "CONFIDENT": f"{attendance.confidence*100:.0f}%" if attendance.confidence else "SIN REGISTRO",
            "DOCENTE": user.nombre if user.rol == "teacher" else ""
        })
    
    df = pd.DataFrame(data)
    
    # Guardar archivo
    filename = f"attendance_report_{fecha_inicio}_{fecha_fin}.{formato}"
    filepath = os.path.join("data/temp", filename)
    
    if formato == "csv":
        df.to_csv(filepath, index=False)
    else:
        df.to_excel(filepath, index=False)
    
    return FileResponse(
        filepath,
        filename=filename,
        media_type=f"application/{formato}"
    )