import os
import sys
import json
import argparse
import cv2
import numpy as np
from manos import DetectorManos

try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    import tensorflow as tf
    Interpreter = tf.lite.Interpreter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_MODELO = os.path.join(BASE_DIR, "modelo", "model.tflite")
RUTA_LABELS = os.path.join(BASE_DIR, "modelo", "labels.txt")


class TraductorSenas:
    def __init__(self, ruta_modelo=RUTA_MODELO, ruta_labels=RUTA_LABELS):
        if not os.path.exists(ruta_modelo) or not os.path.exists(ruta_labels):
            raise FileNotFoundError(
                "No se encontró model.tflite o labels.txt en 'modelo/'. "
                "Ejecuta primero python app/entrenar.py."
            )

        with open(ruta_labels, "r", encoding="utf-8") as f:
            self.etiquetas = [linea.strip() for linea in f if linea.strip()]

        self.interpreter = Interpreter(model_path=ruta_modelo)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predecir(self, vector_landmarks):
        entrada = np.expand_dims(vector_landmarks, axis=0).astype(np.float32)
        self.interpreter.set_tensor(self.input_details[0]["index"], entrada)
        self.interpreter.invoke()
        salida = self.interpreter.get_tensor(self.output_details[0]["index"])[0]

        indice = int(np.argmax(salida))
        confianza = float(salida[indice])
        return self.etiquetas[indice], confianza


def probar_camara(traductor, detector):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara web.")
        return

    print("Probando precisión en vivo. Presiona 'Q' para salir.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        vector, frame_dibujado = detector.procesar_frame(frame, dibujar=True)

        if vector is not None:
            letra, confianza = traductor.predecir(vector)
            color = (0, 255, 0) if confianza >= 0.80 else (0, 165, 255)
            texto = f"Sena: {letra} ({confianza * 100:.1f}%)"
        else:
            color = (150, 150, 150)
            texto = "Sin mano detectada"

        cv2.putText(
            frame_dibujado, texto, (15, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2
        )
        cv2.imshow("Prueba de Precision - Lengua de Senas", frame_dibujado)

        if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
            break

    cap.release()
    cv2.destroyAllWindows()


def procesar_imagen(ruta_imagen, traductor, detector):
    frame = cv2.imread(ruta_imagen)
    if frame is None:
        return {"ok": False, "error": f"No se pudo leer la imagen: {ruta_imagen}"}

    vector, _ = detector.procesar_frame(frame, dibujar=False)
    if vector is None:
        return {"ok": True, "mano_detectada": False, "prediccion": None, "confianza": 0.0}

    letra, confianza = traductor.predecir(vector)
    return {
        "ok": True,
        "mano_detectada": True,
        "prediccion": letra,
        "confianza": round(confianza, 4)
    }


def main():
    parser = argparse.ArgumentParser(description="Traductor de Lengua de Señas CLI")
    parser.add_argument("--camara", action="store_true", help="Abre la cámara para probar precisión en vivo")
    parser.add_argument("--imagen", type=str, help="Ruta a una imagen para traducir y devolver JSON")
    args = parser.parse_args()

    traductor = TraductorSenas()
    detector = DetectorManos(modo_estatico=bool(args.imagen), confianza_deteccion=0.7)

    try:
        if args.camara:
            probar_camara(traductor, detector)
        elif args.imagen:
            resultado = procesar_imagen(args.imagen, traductor, detector)
            print(json.dumps(resultado, ensure_ascii=False))
        else:
            parser.print_help()
    finally:
        detector.cerrar()


if __name__ == "__main__":
    main()