---
name: sign-language-translator
description: Traduce imágenes de lengua de señas (alfabeto dactilológico, letras A-O) a texto estructurado en formato JSON usando visión por computadora. Activar siempre que el usuario envíe una imagen con una mano haciendo una seña o pida interpretar lengua de señas.
---
# Sign Language Translator Skill (V1)

Traduce imágenes de lengua de señas (alfabeto dactilológico, letras A-O) a texto estructurado en formato JSON utilizando visión por computadora (MediaPipe HandLandmarker) y TensorFlow Lite.

Herramienta CLI ligera para detectar articulaciones de la mano (21 puntos clave 3D) y clasificar señas del alfabeto dactilológico desde archivos de imagen, devolviendo una salida JSON limpia lista para ser consumida por agentes de IA.

> **Cuándo activar esta skill:** siempre que el usuario envíe una imagen con una mano haciendo una seña o pida interpretar lengua de señas.

## Alcance del modelo actual (V1)

- **Clases soportadas:** letras de la **`A`** a la **`O`** (15 clases).
- **Entrada:** imagen estática (`.jpg`, `.jpeg`, `.png`, `.webp`) con una mano visible y buena iluminación.
- **Motor:** MediaPipe Tasks (`HandLandmarker`) + TensorFlow Lite (`model.tflite`).

## Instalación de dependencias

Si el entorno aún no tiene las dependencias instaladas (requiere Python 3.12):

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta el traductor pasando la ruta absoluta o relativa de la imagen mediante `--imagen`. Asegúrate de invocar el script apuntando a la ubicación de esta skill:

```bash
python app/traducir.py --imagen "<RUTA_DE_LA_IMAGEN>"
```

> **Nota:** si ejecutas el comando desde fuera de la raíz de esta skill, antepón la ruta base donde está instalada la skill antes de `app/traducir.py`.

## Contrato de salida (JSON)

El script imprime una única línea JSON en `stdout`.

**Detección exitosa:**

```json
{"ok": true, "mano_detectada": true, "prediccion": "B", "confianza": 0.9845}
```

**Sin mano visible en la imagen:**

```json
{"ok": true, "mano_detectada": false, "prediccion": null, "confianza": 0.0}
```

**Error de lectura o ruta inválida:**

```json
{"ok": false, "error": "No se pudo leer la imagen: ruta.jpg"}
```

## Directrices de respuesta para el agente

1. **Umbral de confianza (`0.75`):**
   - Si `confianza >= 0.75`, entrega la letra traducida (`prediccion`) de forma directa y clara.
   - Si `confianza < 0.75`, reporta la letra más probable pero advierte al usuario que la inclinación de la muñeca o la iluminación reducen la certeza, sugiriendo una toma frontal más clara.
2. **Sin mano detectada:** si `mano_detectada` es `false`, indica que no se logró identificar una mano en la imagen y pide que la mano esté bien encuadrada y enfocada.
3. **Encadenamiento multimodal (voz):** si el usuario solicita escuchar la traducción en audio, toma el valor de `prediccion` y pásalo a cualquier herramienta Text-to-Speech (TTS) disponible en tu entorno.
4. **Integridad del modelo:** no ejecutes `app/entrenar.py` ni modifiques los archivos en `modelo/` o `dataset/` a menos que el usuario solicite explícitamente reentrenar o añadir nuevas señas.