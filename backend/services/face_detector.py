import face_recognition
import cv2
import numpy as np
from pathlib import Path
import logging
from core.config import settings
from typing import Tuple, Optional, List

class FaceDetector:
    def __init__(self):
        """
        Inicializa el detector de rostros.
        """
        self.known_face_encodings = []  # Lista de codificaciones conocidas
        self.known_face_ids = []  # Lista de IDs correspondientes a las codificaciones
        self.detection_confidence = settings.FACE_DETECTION_CONFIDENCE
        self.recognition_tolerance = settings.FACE_RECOGNITION_TOLERANCE
        self.logger = logging.getLogger(__name__)

    def load_known_faces(self):
        """
        Carga los rostros conocidos desde el directorio de datasets.
        """
        self.known_face_encodings = []
        self.known_face_ids = []

        dataset_path = Path(settings.DATASET_DIR)

        if not dataset_path.exists():
            self.logger.warning(f"El directorio de datasets no existe: {dataset_path}")
            return

        for user_folder in dataset_path.iterdir():
            if user_folder.is_dir():
                try:
                    user_id = int(user_folder.name.split('_')[1])  # Extraer ID del nombre del directorio

                    for image_path in user_folder.glob('*.jpg'):
                        try:
                            image = face_recognition.load_image_file(str(image_path))
                            encodings = face_recognition.face_encodings(image)

                            if encodings:
                                self.known_face_encodings.append(encodings[0])
                                self.known_face_ids.append(user_id)
                                self.logger.info(f"Rostro cargado: {image_path} para usuario {user_id}")
                            else:
                                self.logger.warning(f"No se encontró codificación en la imagen: {image_path}")

                        except Exception as e:
                            self.logger.error(f"Error al cargar imagen {image_path}: {str(e)}")

                except (IndexError, ValueError):
                    self.logger.error(f"El nombre del directorio no sigue el formato esperado: {user_folder}")

        self.logger.info(f"Total de rostros cargados: {len(self.known_face_encodings)}")

    def get_loaded_users(self) -> List[int]:
        """
        Obtiene una lista de IDs de usuarios con rostros cargados.

        Returns:
            List[int]: Lista de IDs de usuarios.
        """
        return self.known_face_ids

    def detect_faces(self, frame: np.ndarray) -> Tuple[List[int], List[float]]:
        """
        Detecta y reconoce rostros en un frame dado.

        Args:
            frame (np.ndarray): Frame capturado de la cámara.

        Returns:
            Tuple[List[int], List[float]]: Una lista de IDs detectados y una lista de sus respectivas confianzas.
        """
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        detected_ids = []
        confidences = []

        for face_encoding in face_encodings:
            # Comparar la codificación del rostro con las codificaciones conocidas
            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                face_encoding, 
                tolerance=self.recognition_tolerance
            )

            if True in matches:
                # Obtener el índice del primer match verdadero
                match_index = matches.index(True)
                detected_ids.append(self.known_face_ids[match_index])

                # Calcular nivel de confianza
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, 
                    face_encoding
                )
                confidence = 1 - min(face_distances)
                confidences.append(confidence)

        return detected_ids, confidences

    def annotate_frame(self, frame: np.ndarray, detected_ids: List[int], face_locations: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Anota el frame con rectángulos y etiquetas para los rostros detectados.

        Args:
            frame (np.ndarray): Frame capturado de la cámara.
            detected_ids (List[int]): Lista de IDs detectados.
            face_locations (List[Tuple[int, int, int, int]]): Coordenadas de los rostros detectados.

        Returns:
            np.ndarray: Frame anotado.
        """
        for (top, right, bottom, left), user_id in zip(face_locations, detected_ids):
            label = f"User {user_id}"
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)  # Dibujar rectángulo
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)  # Agregar etiqueta

        return frame
