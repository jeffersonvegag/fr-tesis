# backend/api/dependencies.py
from typing import Generator
from sqlalchemy.orm import Session
from core.database import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from services.camera_stream import CameraService
from services.face_detector import FaceDetector
# backend/api/dependencies.py
from db.session import get_db  # Cambiado desde core.database
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_camera_service() -> CameraService:
    camera_service = CameraService()
    if not camera_service.initialize():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo inicializar el servicio de cámara"
        )
    return camera_service

def get_face_detector() -> FaceDetector:
    face_detector = FaceDetector()
    try:
        face_detector.load_known_faces()
        return face_detector
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error al inicializar el detector facial: {str(e)}"
        )