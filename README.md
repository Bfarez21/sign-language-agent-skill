# Sign Language Agent Skill (V1)

Programa que **reconoce letras de la lengua de señas** (alfabeto con las manos, de la **A a la O**) a partir de una foto o de la cámara web.

Le das una imagen de una mano haciendo una seña y te responde con la letra que cree que es y qué tan seguro está.

Funciona de dos formas:

- **Por tu cuenta:** desde tu computadora, sin necesidad de internet ni de una tarjeta gráfica.
- **Con un agente de IA:** como una "skill" que asistentes como Antigravity CLI, Gemini CLI o Claude Code pueden usar.

---

## Contenido

- [Qué necesitas](#qué-necesitas)
- [Cómo usarlo paso a paso](#cómo-usarlo-paso-a-paso)
- [Cómo entender el resultado](#cómo-entender-el-resultado)
- [Consejos para una buena foto](#consejos-para-una-buena-foto)
- [Preguntas frecuentes](#preguntas-frecuentes)
- [Usarlo con un agente de IA](#usarlo-con-un-agente-de-ia)
- [Desarrollo](#desarrollo)
- [Estructura del proyecto](#estructura-del-proyecto)

---

## Qué necesitas

1. Una computadora con **Windows, Mac o Linux**.
2. **Python 3.12** instalado. Puedes descargarlo gratis desde [python.org](https://www.python.org/downloads/). En Windows, marca la casilla **"Add Python to PATH"** durante la instalación.
3. **Git** para descargar el proyecto (descarga en [git-scm.com](https://git-scm.com/downloads)). Si no quieres instalarlo, también puedes descargar el proyecto como ZIP desde GitHub con el botón verde **Code → Download ZIP** y descomprimirlo.
4. Una **foto** de una mano haciendo una seña. Si quieres usar la cámara web, también necesitas una.

---

## Cómo usarlo paso a paso

### Paso 1: Descargar el proyecto

Abre una **terminal**:

- **Windows:** busca "CMD" o "PowerShell" en el menú Inicio.
- **Mac:** abre la app "Terminal".
- **Linux:** abre tu terminal habitual.

Luego copia y pega estos comandos, uno por uno, presionando Enter después de cada uno:

```bash
git clone https://github.com/Bfarez21/sign-language-agent-skill.git
cd sign-language-agent-skill
```

### Paso 2: Traducir una foto

Guarda tu foto dentro de la carpeta del proyecto (por ejemplo, con el nombre `mi_foto.jpg`) y ejecuta:

```bash
python run.py --imagen mi_foto.jpg
```

> **La primera vez tarda más.** El programa se prepara solo e instala lo que necesita (puede demorar unos minutos y requiere internet). Las siguientes veces es casi instantáneo.

También puedes escribir la ruta completa de la foto, por ejemplo: `python run.py --imagen "C:\Users\TuNombre\Fotos\seña.jpg"`.

### Paso 3: Leer la respuesta

Verás una línea como esta:

```json
{"ok": true, "mano_detectada": true, "prediccion": "O", "confianza": 0.9982, "orientacion": "espejo"}
```

Aquí te explicamos cómo leerla.

### Opcional: Probar con la cámara web

Para ver la detección en vivo con tu cámara:

```bash
python app/traducir.py --camara
```

- Presiona **`S`** para guardar una foto como `prueba.jpg`.
- Presiona **`Q`** para salir.

> Este modo requiere que ya se hayan instalado las dependencias (basta con haber hecho el Paso 2 al menos una vez).

---

## Cómo entender el resultado

La respuesta es una línea con varios datos. Los importantes son estos:

| Dato | Qué significa |
| --- | --- |
| `"ok": true` | Todo funcionó bien. Si dice `false`, hubo un problema (el motivo aparece en `error`). |
| `"mano_detectada": true` | Encontró una mano en la foto. Si dice `false`, no vio ninguna. |
| `"prediccion": "O"` | La **letra** que reconoció. |
| `"confianza": 0.9982` | Qué tan seguro está, de 0 a 1. Aquí es **99.8 %**. |
| `"orientacion"` | Indica si acertó con la foto tal cual (`original`) o volteada como espejo (`espejo`). No necesitas hacer nada con este dato. |

**Regla simple:** si la confianza es **0.75 (75 %) o más**, la letra es confiable. Si es menor, trata el resultado como una pista y prueba con otra foto.

### Otros resultados posibles

**No encontró una mano:**

```json
{"ok": true, "mano_detectada": false, "prediccion": null, "confianza": 0.0}
```

**No pudo abrir la foto** (por ejemplo, el nombre está mal escrito):

```json
{"ok": false, "error": "No se pudo leer la imagen: mi_foto.jpg"}
```

---

## Consejos para una buena foto

- **Buena luz:** evita fotos oscuras o con mucho contraste.
- **De frente:** la palma o la seña debe mirar hacia la cámara, sin inclinar mucho la muñeca.
- **Mano completa:** que se vean todos los dedos y que no quede cortada en el borde.
- **Una sola mano:** evita que aparezcan otras manos en la imagen.
- **Bien enfocada:** una foto borrosa o con movimiento reduce la confianza.
- **Formatos aceptados:** `.jpg`, `.jpeg`, `.png` y `.webp`.

---

## Preguntas frecuentes

**¿Por qué dice que no detecta ninguna mano?**
Casi siempre es por poca luz, una foto borrosa o una mano cortada. Prueba con una foto más clara, de frente y con la mano completa.

**¿Por qué la confianza es baja?**
La seña puede estar inclinada o la foto poco nítida. Toma otra más frontal.

**¿Reconoce todas las letras?**
Por ahora solo de la **A a la O** (15 letras). Las demás se pueden agregar; mira la sección [Desarrollo](#desarrollo).

**¿Reconoce palabras o frases?**
No, solo letras individuales a partir de una imagen.

**¿Necesito internet?**
Solo la primera vez, para descargar el proyecto y lo que necesita. Después funciona sin conexión.

**La cámara web no abre.**
Cierra otras aplicaciones que puedan estar usándola (videollamadas, por ejemplo) y vuelve a intentarlo.

**Me aparece un error de "python no se reconoce".**
Python no está instalado o no se agregó al PATH. Reinstálalo marcando **"Add Python to PATH"**.

---

## Usarlo con un agente de IA

Si usas un asistente de IA en la terminal, puedes instalar este proyecto como una **skill** para que lo use por ti: le envías una imagen y te responde con la letra.

Descarga el proyecto dentro de la carpeta de skills de tu agente.

### Antigravity CLI (`agy`)

**Windows (CMD / PowerShell):**

```cmd
git clone https://github.com/Bfarez21/sign-language-agent-skill.git "%USERPROFILE%\.gemini\antigravity-cli\skills\sign-language-translator"
```

**Linux / macOS:**

```bash
git clone https://github.com/Bfarez21/sign-language-agent-skill.git ~/.gemini/antigravity-cli/skills/sign-language-translator
```

Luego abre `agy` y ejecuta `/skills reload` (o reinicia la sesión).

### Gemini CLI y otros agentes compatibles

```bash
git clone https://github.com/Bfarez21/sign-language-agent-skill.git ~/.gemini/skills/sign-language-translator
```

> Las instrucciones que sigue el agente están en [`SKILL.md`](SKILL.md).

---

## Desarrollo

Esta sección es para quienes quieran modificar el proyecto o agregar nuevas letras. Si solo quieres usar el traductor, **no la necesitas**.

### Preparar el entorno manualmente

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements-train.txt
```

### Comandos principales

| Comando | Para qué sirve |
| --- | --- |
| `python app/traducir.py --imagen foto.jpg` | Traduce una foto. |
| `python app/traducir.py --camara` | Prueba en vivo con la cámara web. |
| `python app/capturar.py` | Graba nuevas muestras de una seña con la cámara. |
| `python app/entrenar.py` | Entrena el modelo con las muestras grabadas. |

### Comprobar que todo funciona

Prueba estos tres casos con `python app/traducir.py --imagen <archivo>`:

| Prueba | Resultado esperado |
| --- | --- |
| Una foto con una mano | `"mano_detectada": true` y una letra en `prediccion`. |
| Una foto sin manos (un paisaje, por ejemplo) | `"mano_detectada": false`. |
| Un archivo que no existe | `"ok": false` con un mensaje de error. |

### Agregar nuevas letras (P–Z)

1. Instala las herramientas de entrenamiento:

   ```bash
   pip install -r requirements-train.txt
   ```

2. Graba unas **150 muestras** de la nueva seña, variando un poco la posición y la distancia:

   ```bash
   python app/capturar.py
   ```

3. Entrena el nuevo modelo:

   ```bash
   python app/entrenar.py
   ```

4. Prueba con `python app/traducir.py --imagen foto.jpg` para confirmar que reconoce la nueva letra.

---

## Estructura del proyecto

```text
sign-language-agent-skill/
├── SKILL.md                 # Instrucciones para el agente de IA
├── run.py                   # Lanzador automático (prepara todo la primera vez)
├── requirements.txt         # Lo necesario para traducir
├── requirements-train.txt   # Lo necesario para entrenar y capturar
├── app/
│   ├── traducir.py          # Traduce fotos o usa la cámara
│   ├── manos.py             # Detecta la mano y sus 21 puntos
│   ├── capturar.py          # Graba muestras de nuevas señas
│   └── entrenar.py          # Entrena el modelo
├── modelo/
│   ├── model.tflite         # Modelo entrenado (letras A–O)
│   ├── labels.txt           # Lista de letras que conoce
│   └── hand_landmarker.task # Modelo base de detección de manos
└── dataset/                 # Muestras de entrenamiento (no se sube a Git)
```

---

## ¿Cómo funciona por dentro? 

En lugar de analizar la foto completa, el programa:

1. **Detecta la mano** y ubica sus 21 puntos (articulaciones y puntas de los dedos) con MediaPipe.
2. **Ajusta los puntos** para que no importe qué tan cerca o lejos esté la mano de la cámara.
3. **Clasifica la seña** con un modelo pequeño de TensorFlow Lite, en milisegundos y sin necesitar tarjeta gráfica.