# backend/api/endpoints/recognition.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio  # Agregamos esta importación
import cv2
import numpy as np
from pathlib import Path
import logging
from core.config import settings
import time
import face_recognition
from core.database import get_db
from services.face_detector import FaceDetector
from services.camera_stream import CameraService
from services.attendance_manager import AttendanceManager
import io
from models.user import User
from typing import List, Optional, Tuple  # Agregar List si no está presente



router = APIRouter()
face_detector = FaceDetector()
camera_service = CameraService()
logger = logging.getLogger(__name__)

@router.get("/rtsp/test")
async def test_rtsp_connection():
    """
    Prueba la conexión RTSP y devuelve el estado
    """
    try:
        if camera_service.initialize():
            frame = camera_service.get_frame()
            camera_service.release()
            
            if frame is not None:
                return {"status": "success", "message": "Conexión RTSP establecida y frame capturado exitosamente"}
            else:
                return {"status": "error", "message": "Conexión establecida pero no se pudo leer el frame"}
        else:
            return {"status": "error", "message": "No se pudo establecer conexión con la cámara RTSP"}
    except Exception as e:
        logger.error(f"Error al probar conexión RTSP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al conectar con RTSP: {str(e)}")

@router.get("/rtsp/frame")
async def get_current_frame():
    """
    Obtiene y devuelve el frame actual de la cámara RTSP
    """
    try:
        if not camera_service.initialize():
            raise HTTPException(status_code=500, detail="No se pudo conectar a la cámara RTSP")
        
        frame = camera_service.get_frame()
        camera_service.release()
        
        if frame is None:
            raise HTTPException(status_code=500, detail="No se pudo leer el frame de la cámara")
        
        return StreamingResponse(io.BytesIO(frame), media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error al obtener frame RTSP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener frame: {str(e)}")

@router.get("/rtsp/status")
async def get_rtsp_status():
    """
    Obtiene información detallada sobre el estado de la conexión RTSP
    """
    try:
        if not camera_service.initialize():
            return {"status": "error", "message": "No se pudo conectar a la cámara"}
        
        cap = camera_service.cap
        status = {
            "is_connected": cap.isOpened(),
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "frame_height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "backend": cap.getBackendName(),
            "rtsp_url": settings.RTSP_URL
        }
        camera_service.release()
        return status
    except Exception as e:
        logger.error(f"Error al obtener estado RTSP: {str(e)}")
        return {"status": "error", "message": str(e)}

# Tus endpoints existentes continúan aquí...
@router.post("/dataset/capture/{user_id}")
async def capture_dataset(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Captura imágenes para el dataset de entrenamiento
    """
    logger.info(f"Iniciando captura de dataset para usuario {user_id}")
    
    if not camera_service.initialize():
        raise HTTPException(
            status_code=500,
            detail="Error al inicializar la cámara"
        )
    
    user_dir = Path(settings.DATASET_DIR) / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    
    image_count = 0
    start_time = time.time()
    
    try:
        logger.info("Iniciando captura de imágenes...")
        while image_count < 10:  # Capturar 10 imágenes
            frame = camera_service.get_frame()
            if frame is None:
                logger.warning("No se pudo obtener frame de la cámara")
                continue
            
            # Convertir bytes a numpy array
            nparr = np.frombuffer(frame, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.warning("No se pudo decodificar la imagen")
                continue
                
            # Detectar rostros
            faces = face_recognition.face_locations(img)
            if len(faces) == 1:  # Asegurar que solo hay un rostro
                image_path = user_dir / f"user.{user_id}.{image_count+1}.jpg"
                logger.info(f"Guardando imagen {image_count+1} en {image_path}")
                cv2.imwrite(str(image_path), img)
                image_count += 1
                time.sleep(settings.CAPTURE_INTERVAL)
            else:
                logger.warning(f"Se detectaron {len(faces)} rostros en el frame, se esperaba 1")
            
            if time.time() - start_time > 30:  # Timeout después de 30 segundos
                logger.warning("Timeout en la captura de imágenes")
                break
    
    except Exception as e:
        logger.error(f"Error durante la captura: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error durante la captura de imágenes: {str(e)}"
        )
    finally:
        camera_service.release()
        logger.info(f"Captura finalizada. Se capturaron {image_count} imágenes")
    
    return {
        "message": f"Capturadas {image_count} imágenes",
        "images_captured": image_count,
        "directory": str(user_dir)
    }

@router.post("/recognition/train")
async def train_recognition():
    try:
        face_detector.load_known_faces()
        return {"message": "Entrenamiento completado exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante el entrenamiento: {str(e)}"
        )
@router.get("/recognition/loaded_users", response_model=List[int])
async def get_loaded_users():
    """
    Obtiene una lista de los IDs de usuarios cuyos rostros están cargados en memoria.
    """
    try:
        if not face_detector.known_face_ids:
            return []
        return face_detector.known_face_ids
    except Exception as e:
        logger.error(f"Error al obtener usuarios cargados: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuarios cargados: {str(e)}"
        )


@router.get("/recognition/stream")
async def get_recognition_stream():
    if not camera_service.initialize():
        raise HTTPException(
            status_code=500,
            detail="Error al inicializar la cámara"
        )

    async def generate():
        try:
            while True:
                frame = camera_service.get_frame()
                if frame is None:
                    continue

                # Convertir bytes a numpy array
                nparr = np.frombuffer(frame, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Detectar rostros
                face_locations = face_recognition.face_locations(img)
                for (top, right, bottom, left) in face_locations:
                    # Recortar el rostro detectado
                    face_img = img[top:bottom, left:right]

                    # Codificar la imagen recortada como JPEG
                    ret, buffer = cv2.imencode('.jpg', face_img)
                    if ret:
                        yield (b'--frame\r\n'
                              b'Content-Type: image/jpeg\r\n\r\n' +
                              buffer.tobytes() +
                              b'\r\n')

                await asyncio.sleep(0.1)  # Pausa para no sobrecargar

        finally:
            camera_service.release()

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
@router.get("/recognition/html", response_class=HTMLResponse)
async def serve_recognition_page():
    """
    Endpoint para servir la página HTML que muestra el stream de rostros detectados.
    """
    # Ruta relativa del archivo HTML
    template_path = Path("backend/templates/stream.html")
    
    if not template_path.exists():
        # Si el archivo HTML no existe, devuelve un mensaje de error
        return HTMLResponse(content="<h1>El archivo HTML no se encontró</h1>", status_code=404)
    
    # Leer y devolver el contenido del archivo HTML
    return template_path.read_text()


@router.get("/rtsp/detect")
async def detect_face():
    """
    Detecta el rostro y lo compara con los rostros conocidos
    """
    try:
        if not camera_service.initialize():
            raise HTTPException(status_code=500, detail="No se pudo inicializar la cámara")

        frame = camera_service.get_frame()
        camera_service.release()

        if frame is None:
            raise HTTPException(status_code=500, detail="No se pudo capturar el frame")

        # Convertir el frame a numpy array
        nparr = np.frombuffer(frame, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Detectar rostros en el frame
        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)

        if not face_encodings:
            return {"message": "No se detectaron rostros"}

        # Comparar el rostro detectado con los rostros conocidos
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                face_detector.known_face_encodings, face_encoding, tolerance=0.7
            )
            face_distances = face_recognition.face_distance(
                face_detector.known_face_encodings, face_encoding
            )

            if True in matches:
                match_index = matches.index(True)
                user_id = face_detector.known_face_ids[match_index]
                
                # Recuperar el usuario de la base de datos
                db = next(get_db())
                user = db.query(User).filter(User.id == user_id).first()

                if user:
                    return {
                        "message": "Rostro detectado",
                        "user_id": user.id,
                        "nombre": user.nombre,
                        "apellido": user.apellido,
                        "rol": user.rol.value,
                    }

        return {"message": "Rostro detectado, pero no coincide con ningún usuario registrado"}

    except Exception as e:
        logger.error(f"Error durante la detección: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error durante la detección: {str(e)}")
