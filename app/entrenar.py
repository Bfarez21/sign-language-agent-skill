import os
import glob
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

CARPETA_DATASET = "dataset"
CARPETA_MODELO = "modelo"
RUTA_TFLITE = os.path.join(CARPETA_MODELO, "model.tflite")
RUTA_LABELS = os.path.join(CARPETA_MODELO, "labels.txt")


def cargar_datos():
    archivos = sorted(glob.glob(os.path.join(CARPETA_DATASET, "*.npy")))
    if not archivos:
        raise FileNotFoundError(
            f"No se encontraron archivos .npy en '{CARPETA_DATASET}/'. "
            "Ejecuta primero app/capturar.py."
        )

    X = []
    y = []
    etiquetas = []

    for indice, ruta in enumerate(archivos):
        nombre_etiqueta = os.path.splitext(os.path.basename(ruta))[0]
        etiquetas.append(nombre_etiqueta)

        muestras = np.load(ruta)
        X.append(muestras)
        y.extend([indice] * len(muestras))
        print(f"Cargada clase '{nombre_etiqueta}': {len(muestras)} muestras")

    X = np.vstack(X).astype(np.float32)
    y = np.array(y, dtype=np.int32)
    return X, y, etiquetas


def normalizar_lote(puntos):
    # Centra en la muñeca (punto 0) y escala por la distancia máxima
    puntos = puntos - puntos[:, 0:1, :]
    max_dist = np.max(np.linalg.norm(puntos, axis=2), axis=1, keepdims=True)
    max_dist = np.maximum(max_dist, 1e-6)[:, :, np.newaxis]
    return puntos / max_dist


def aumentar_datos(X, y, copias=6):
    X_aug = [X]
    y_aug = [y]

    for i in range(copias):
        puntos = X.reshape(-1, 21, 3).copy()

        # En la mitad de las copias, invierte lateralidad (mano izq/der y espejo)
        if i % 2 == 1:
            puntos[:, :, 0] *= -1.0

        # Ángulos aleatorios entre -20 y +20 grados en radianes
        ang_x = np.random.uniform(-0.35, 0.35, size=(len(puntos), 1))
        ang_y = np.random.uniform(-0.35, 0.35, size=(len(puntos), 1))
        ang_z = np.random.uniform(-0.30, 0.30, size=(len(puntos), 1))

        # Rotación eje X
        y_coord = puntos[:, :, 1] * np.cos(ang_x) - puntos[:, :, 2] * np.sin(ang_x)
        z_coord = puntos[:, :, 1] * np.sin(ang_x) + puntos[:, :, 2] * np.cos(ang_x)
        puntos[:, :, 1], puntos[:, :, 2] = y_coord, z_coord

        # Rotación eje Y
        x_coord = puntos[:, :, 0] * np.cos(ang_y) + puntos[:, :, 2] * np.sin(ang_y)
        z_coord = -puntos[:, :, 0] * np.sin(ang_y) + puntos[:, :, 2] * np.cos(ang_y)
        puntos[:, :, 0], puntos[:, :, 2] = x_coord, z_coord

        # Rotación eje Z
        x_coord = puntos[:, :, 0] * np.cos(ang_z) - puntos[:, :, 1] * np.sin(ang_z)
        y_coord = puntos[:, :, 0] * np.sin(ang_z) + puntos[:, :, 1] * np.cos(ang_z)
        puntos[:, :, 0], puntos[:, :, 1] = x_coord, y_coord

        # Pequeño ruido de sensor y re-normalización exacta
        puntos += np.random.normal(0, 0.008, size=puntos.shape)
        puntos = normalizar_lote(puntos)

        X_aug.append(puntos.reshape(-1, 63).astype(np.float32))
        y_aug.append(y)

    return np.vstack(X_aug), np.concatenate(y_aug)


def construir_modelo(num_clases):
    modelo = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(63,)),
        tf.keras.layers.Dense(256, activation="relu"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.25),

        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.25),

        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.15),

        tf.keras.layers.Dense(num_clases, activation="softmax")
    ])

    modelo.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return modelo


def main():
    os.makedirs(CARPETA_MODELO, exist_ok=True)
    X, y, etiquetas = cargar_datos()
    num_clases = len(etiquetas)

    if num_clases < 2:
        print("Error: Necesitas al menos 2 letras distintas en dataset/ para entrenar.")
        return

    # Dividir 80% entrenamiento y 20% validación
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Generar rotaciones 3D + espejo solo sobre entrenamiento
    X_train, y_train = aumentar_datos(X_train, y_train, copias=6)

    print(f"\nEntrenando modelo con {num_clases} clases ({len(X_train)} muestras de entrenamiento)...")
    modelo = construir_modelo(num_clases)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=12, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=5, min_lr=1e-5
        ),
    ]

    modelo.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )

    loss, acc = modelo.evaluate(X_val, y_val, verbose=0)
    print(f"\nPrecisión global en validación: {acc * 100:.2f}%\n")

    # Reporte detallado por letra para detectar posibles confusiones
    y_pred = np.argmax(modelo.predict(X_val, verbose=0), axis=1)
    print(classification_report(y_val, y_pred, target_names=etiquetas, digits=3))

    # Exportar a TensorFlow Lite
    converter = tf.lite.TFLiteConverter.from_keras_model(modelo)
    tflite_model = converter.convert()

    with open(RUTA_TFLITE, "wb") as f:
        f.write(tflite_model)

    with open(RUTA_LABELS, "w", encoding="utf-8") as f:
        for etiqueta in etiquetas:
            f.write(f"{etiqueta}\n")

    print(f"Modelo guardado en: {RUTA_TFLITE}")
    print(f"Etiquetas guardadas en: {RUTA_LABELS}")


if __name__ == "__main__":
    main()