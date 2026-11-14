---
name: sign-language-translator
description: Traduce imágenes de lengua de señas (alfabeto dactilológico, letras A-O) a texto estructurado en formato JSON usando visión por computadora. Activar siempre que el usuario envíe una imagen con una mano haciendo una seña o pida interpretar lengua de señas.
---

# Sign Language Translator (V1)

Herramienta CLI ligera que detecta 21 puntos clave 3D de la mano (MediaPipe `HandLandmarker`) y clasifica señas del alfabeto dactilológico (letras **A–O**) mediante TensorFlow Lite, devolviendo una salida JSON limpia lista para ser consumida por agentes de IA.

## Alcance y requisitos

- **Clases soportadas:** letras **`A`** a la **`O`** (15 clases).
- **Entrada:** imagen estática (`.jpg`, `.jpeg`, `.png`, `.webp`) con una mano visible y buena iluminación.
- **Entorno:** Python 3.12 (el lanzador `run.py` detecta o crea automáticamente el entorno virtual `.venv` e instala `requirements.txt` si hace falta).

## Ejecución (para el agente)

Ejecuta `run.py` en un **único comando directo** pasando la ruta de la imagen con `--imagen`. No busques intérpretes manualmente ni inspecciones otros archivos `.py` antes de ejecutar:

```bash
python run.py --imagen "<RUTA_DE_LA_IMAGEN>"
```

**Linux / macOS:**

```bash
.venv/bin/python app/traducir.py --imagen "<RUTA_DE_LA_IMAGEN>"
```

> **Nota de ruta:** si el agente se encuentra en otro directorio de trabajo, antepón la ruta base de esta skill tanto al ejecutable de `.venv` como a `app/traducir.py`. Si no existe `.venv` local, usa el entorno virtual configurado en el sistema (por ejemplo `C:\venvs\sign-lang\Scripts\python.exe`).

## Contrato de salida (JSON)

El script devuelve una única línea JSON en `stdout`:

| Estado | Ejemplo de salida |
| --- | --- |
| Detección exitosa | `{"ok": true, "mano_detectada": true, "prediccion": "B", "confianza": 0.9845, "orientacion": "original"}` |
| Sin mano visible | `{"ok": true, "mano_detectada": false, "prediccion": null, "confianza": 0.0}` |
| Error de lectura | `{"ok": false, "error": "No se pudo leer la imagen: ruta.jpg"}` |

## Reglas de respuesta para el agente

1. **Umbral de confianza (`0.75`):**
   - Si `confianza >= 0.75`: responde de forma directa y concisa con la letra detectada (`prediccion`).
   - Si `confianza < 0.75`: indica la letra más probable, pero advierte que la iluminación o el ángulo reducen la certeza y sugiere una foto frontal más clara.
2. **Sin mano detectada (`mano_detectada: false`):** informa que no se detectó ninguna mano y pide una imagen bien enfocada y encuadrada.
3. **Salida en audio (TTS):** si el usuario pide escuchar la traducción, envía el valor de `prediccion` a la herramienta Text-to-Speech disponible en el entorno.
4. **Protección del modelo:** nunca ejecutes `app/entrenar.py` ni alteres `modelo/` o `dataset/` salvo petición explícita del usuario.