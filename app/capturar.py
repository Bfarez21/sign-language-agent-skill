import os
import cv2
import numpy as np
from manos import DetectorManos

CARPETA_DATASET = "dataset"
MUESTRAS_POR_LETRA = 150


def main():
    os.makedirs(CARPETA_DATASET, exist_ok=True)
    letra = input("Ingresa la letra o seña a capturar (ej. A, B, C): ").strip().upper()
    if not letra:
        print("Etiqueta vacía. Saliendo.")
        return

    ruta_archivo = os.path.join(CARPETA_DATASET, f"{letra}.npy")
    detector = DetectorManos(modo_estatico=False, confianza_deteccion=0.7)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara web.")
        return

    grabando = False
    muestras = []

    print(f"\nListo para capturar '{letra}'.")
    print("Presiona 'G' en la ventana de video para empezar a grabar.")
    print("Presiona 'Q' para salir sin guardar.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Efecto espejo para que sea natural moverse frente a la cámara
        frame = cv2.flip(frame, 1)
        vector, frame_dibujado = detector.procesar_frame(frame, dibujar=True)

        if grabando:
            if vector is not None:
                muestras.append(vector)
            estado_texto = f"GRABANDO '{letra}': {len(muestras)}/{MUESTRAS_POR_LETRA}"
            color = (0, 0, 255)  # Rojo
        else:
            estado_texto = f"Letra '{letra}' | Presiona 'G' para grabar"
            color = (0, 255, 0)  # Verde

        cv2.putText(
            frame_dibujado, estado_texto, (15, 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
        )
        cv2.imshow("Captura de Dataset - Lengua de Senas", frame_dibujado)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('g') or tecla == ord('G'):
            grabando = True
        elif tecla == ord('q') or tecla == ord('Q'):
            print("Captura cancelada.")
            break

        if len(muestras) >= MUESTRAS_POR_LETRA:
            datos_np = np.array(muestras, dtype=np.float32)
            np.save(ruta_archivo, datos_np)
            print(f"Éxito Se guardaron {len(muestras)} muestras en '{ruta_archivo}'.")
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.cerrar()


if __name__ == "__main__":
    main()