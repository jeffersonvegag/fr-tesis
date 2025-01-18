# backend/api/config.py
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional
import os

class APISettings(BaseSettings):
    # Configuración de la API
    API_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Reconocimiento Facial"
    DEBUG: bool = True

    # Configuración de seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días

    # Configuración de la base de datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@db:5432/face_recognition_db"
    )

    # Configuración de directorios
    BASE_PATH: Path = Path(__file__).resolve().parent.parent
    DATASET_PATH: Path = BASE_PATH / "data/dataset/users"
    TEMP_PATH: Path = BASE_PATH / "data/dataset/temp"

    # Configuración de la cámara
    RTSP_URL: str = "rtsp://admin:tesis123@192.168.100.27:554/cam/realmonitor?channel=1&subtype=1"
    CAMERA_TIMEOUT: int = 30  # segundos
    FRAME_INTERVAL: float = 0.5  # segundos

    # Configuración del reconocimiento facial
    FACE_DETECTION_CONFIDENCE: float = 0.5
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    MIN_FACE_SIZE: int = 20
    MAX_FACE_SIZE: int = 1000

    class Config:
        case_sensitive = True
        env_file = ".env"

api_settings = APISettings()