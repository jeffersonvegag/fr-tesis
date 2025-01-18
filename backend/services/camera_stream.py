# backend/services/camera_stream.py
import cv2
import time
from core.config import settings
import logging
from typing import Generator, Optional

# services/camera_stream.py
class CameraService:
    def __init__(self):
        self.rtsp_url = settings.RTSP_URL
        self.cap = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)

    def initialize(self) -> bool:
        try:
            self.logger.info(f"Inicializando cámara con URL: {self.rtsp_url}")
            self.cap = cv2.VideoCapture(self.rtsp_url)
            if not self.cap.isOpened():
                self.logger.error("No se pudo conectar a la cámara RTSP")
                return False
            self.is_running = True
            self.logger.info("Cámara inicializada correctamente")
            return True
        except Exception as e:
            self.logger.error(f"Error al inicializar la cámara: {str(e)}")
            return False

    def get_frame(self) -> Optional[bytes]:
        if not self.is_running or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        ret, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes() if ret else None

    def release(self):
        if self.cap:
            self.cap.release()
            self.is_running = False
            self.logger.info("Cámara liberada")