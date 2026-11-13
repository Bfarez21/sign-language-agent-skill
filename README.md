# Sign Language Agent Skill

Motor de reconocimiento de lengua de señas (alfabeto dactilológico, letras **A–O**) construido en Python con visión por computadora y aprendizaje profundo ligero, empaquetado como una **CLI Skill** lista para ser consumida por agentes de IA o integrada en aplicaciones externas.

---

## ¿Qué resuelve este proyecto?

La mayoría de los modelos de reconocimiento de señas dependen de redes convolucionales pesadas sobre imágenes completas, lo que los hace lentos, sensibles al fondo y difíciles de ejecutar sin GPU.

Este proyecto adopta un enfoque geométrico mucho más rápido y ligero:

1. **Extracción de esqueleto 3D:** usa **MediaPipe Tasks (`HandLandmarker`)** para detectar los 21 puntos articulados de la mano en coordenadas `(x, y, z)`.
2. **Normalización invariante:** centra los puntos respecto a la muñeca (origen `0,0,0`) y normaliza la escala, logrando que la detección no dependa de la distancia a la cámara ni de la posición en el encuadre.
3. **Clasificación ligera:** un perceptrón multicapa exportado a **TensorFlow Lite / LiteRT (`model.tflite`)** clasifica el vector de 63 características en milisegundos sobre CPU y devuelve el resultado en formato JSON.

---

## Arquitectura del repositorio

```text
sign-language-agent-skill/
├── app/
│   ├── manos.py               # Detector de landmarks 3D y normalización geométrica
│   ├── capturar.py            # Captura de muestras de entrenamiento desde webcam
│   ├── entrenar.py            # Entrenamiento con Data Augmentation 3D y exportación TFLite
│   └── traducir.py            # Interfaz CLI (inferencia sobre imagen o webcam en vivo)
├── modelo/
│   ├── model.tflite           # Red neuronal entrenada (V1: letras A–O)
│   └── labels.txt             # Mapa de clases del modelo
├── dataset/                   # Carpeta local para muestras .npy (excluida de Git)
├── SKILL.md                   # Especificación de integración para agentes de IA
├── requirements.txt           # Dependencias ligeras de ejecución
└── requirements-train.txt     # Dependencias para captura y entrenamiento
```

---

## Inicio rápido

### 1. Clonar e instalar dependencias

Requiere Python 3.12.

```bash
git clone https://github.com/Bfarez21/sign-language-agent-skill.git
cd sign-language-agent-skill

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Probar en tiempo real con tu cámara

```bash
python app/traducir.py --camara
```

### 3. Ejecutar predicción sobre una imagen

```bash
python app/traducir.py --imagen ruta/de/imagen.jpg
```

Salida generada:

```json
{"ok": true, "mano_detectada": true, "prediccion": "B", "confianza": 0.9942}
```

---

## Entrenamiento y escalabilidad

El modelo actual (V1) reconoce las letras de la A a la O (15 clases), entrenado con muestras propias y rotaciones 3D sintéticas para mejorar la tolerancia ante inclinaciones de muñeca.

Para añadir las letras restantes (P–Z) o nuevas señas:

1. Instala las herramientas de entrenamiento: `pip install -r requirements-train.txt`
2. Graba nuevas muestras con `python app/capturar.py`
3. Reentrena el modelo con `python app/entrenar.py`

> Para detalles sobre cómo conectar esta herramienta como Skill dentro de un agente autónomo, consulta [`SKILL.md`](SKILL.md).