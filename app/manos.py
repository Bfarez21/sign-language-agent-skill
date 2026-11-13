import os
import urllib.request
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

URL_MODELO_MANO = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
RUTA_MODELO_MANO = os.path.join("modelo", "hand_landmarker.task")

# Conexiones entre los 21 puntos de la mano para dibujar el esqueleto
CONEXIONES_MANO = [
    (0, 1), (1, 2), (2, 3), (3, 4),           # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),           # Índice
    (5, 9), (9, 10), (10, 11), (11, 12),      # Medio
    (9, 13), (13, 14), (14, 15), (15, 16),    # Anular
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)  # Meñique y palma
]


def _asegurar_modelo_mano():
    os.makedirs(os.path.dirname(RUTA_MODELO_MANO), exist_ok=True)
    if not os.path.exists(RUTA_MODELO_MANO):
        print("Descargando modelo oficial de detección de manos (hand_landmarker.task)...")
        urllib.request.urlretrieve(URL_MODELO_MANO, RUTA_MODELO_MANO)
        print("Descarga completada.")


class DetectorManos:
    def __init__(self, modo_estatico=False, confianza_deteccion=0.7):
        _asegurar_modelo_mano()

        base_options = python.BaseOptions(model_asset_path=RUTA_MODELO_MANO)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=confianza_deteccion,
            min_hand_presence_confidence=confianza_deteccion,
            min_tracking_confidence=0.5,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def _dibujar_landmarks(self, frame, hand_landmarks):
        alto, ancho, _ = frame.shape
        coordenadas_px = []

        for lm in hand_landmarks:
            cx, cy = int(lm.x * ancho), int(lm.y * alto)
            coordenadas_px.append((cx, cy))

        # Dibujar líneas
        for inicio, fin in CONEXIONES_MANO:
            cv2.line(frame, coordenadas_px[inicio], coordenadas_px[fin], (0, 255, 0), 2)

        # Dibujar articulaciones
        for cx, cy in coordenadas_px:
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

    def procesar_frame(self, frame, dibujar=False):
        """
        Recibe un frame BGR de OpenCV.
        Retorna:
          - vector_normalizado: np.ndarray de forma (63,) o None si no hay mano.
          - frame_salida: imagen con puntos dibujados si dibujar=True.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        resultados = self.detector.detect(mp_image)

        frame_salida = frame.copy() if dibujar else frame

        if not resultados.hand_landmarks:
            return None, frame_salida

        hand_landmarks = resultados.hand_landmarks[0]

        if dibujar:
            self._dibujar_landmarks(frame_salida, hand_landmarks)

        # Extraer las 21 coordenadas (x, y, z) -> matriz (21, 3)
        puntos = np.array(
            [[lm.x, lm.y, lm.z] for lm in hand_landmarks],
            dtype=np.float32
        )

        # 1. Traslación: muñeca (índice 0) como origen (0, 0, 0)
        muneca = puntos[0].copy()
        puntos_relativos = puntos - muneca

        # 2. Escala: dividir por la distancia máxima
        max_valor = np.max(np.abs(puntos_relativos))
        if max_valor > 0:
            puntos_normalizados = puntos_relativos / max_valor
        else:
            puntos_normalizados = puntos_relativos

        return puntos_normalizados.flatten(), frame_salida

    def cerrar(self):
        self.detector.close()