from pydantic_settings import BaseSettings
import os
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # Configuración básica de la aplicación
    PROJECT_NAME: str = "Sistema de Reconocimiento Facial"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    DEBUG: bool = os.getenv("DEBUG", True)
    
    # Configuración de la base de datos
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "face_recognition_db")
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    # Configuración de seguridad
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días
    ALGORITHM: str = "HS256"
    
    # Configuración de la cámara RTSP
    RTSP_URL: str = os.getenv(
        "RTSP_URL",
        "rtsp://admin:tesis123@192.168.100.27:554/cam/realmonitor?channel=1&subtype=1"
    )
    CAMERA_TIMEOUT: int = 30  # segundos
    FRAME_INTERVAL: float = 0.5  # segundos
    
    # Configuración de directorios
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATASET_DIR: Path = BASE_DIR / "data/dataset/users"
    TEMP_DIR: Path = BASE_DIR / "data/dataset/temp"
    MODELS_DIR: Path = BASE_DIR / "data/models"
    
    # Configuración del reconocimiento facial
    FACE_DETECTION_CONFIDENCE: float = 0.5
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    CAPTURE_INTERVAL: float = 0.5  # Intervalo de captura en segundos
    MIN_FACE_SIZE: int = 20
    MAX_FACE_SIZE: int = 1000
    MAX_FACES_PER_IMAGE: int = 1
    
    # Configuración de la asistencia
    ATTENDANCE_CONFIDENCE_THRESHOLD: float = 0.65  # Umbral mínimo de confianza para marcar asistencia
    ATTENDANCE_TIME_WINDOW: int = 15  # Ventana de tiempo en minutos para registrar asistencia
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuración de CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

    def get_cors_origins(self) -> list:
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS

settings = Settings()