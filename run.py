import os
import sys
import subprocess
import venv
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, ".venv")
REQ_FILE = os.path.join(BASE_DIR, "requirements.txt")
SCRIPT_TRADUCIR = os.path.join(BASE_DIR, "app", "traducir.py")


def obtener_python_venv():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def entorno_actual_listo():
    return (
        importlib.util.find_spec("cv2") is not None
        and importlib.util.find_spec("mediapipe") is not None
    )


def asegurar_entorno():
    # 1. Si el Python actual ya tiene las dependencias instaladas, úsalo directo
    if entorno_actual_listo():
        return sys.executable

    # 2. Verificar entornos preexistentes (variable de entorno o ruta local conocida)
    rutas_existentes = [
        os.environ.get("SIGN_LANG_PYTHON", ""),
        r"C:\venvs\sign-lang\Scripts\python.exe",
    ]
    for ruta in rutas_existentes:
        if ruta and os.path.exists(ruta):
            return ruta

    # 3. Si no hay ningún entorno previo, crea .venv e instala dependencias (Plug & Play)
    py_venv = obtener_python_venv()
    if not os.path.exists(py_venv):
        venv.create(VENV_DIR, with_pip=True)
        subprocess.run(
            [py_venv, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-r", REQ_FILE],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    return py_venv


if __name__ == "__main__":
    python_ejecutable = asegurar_entorno()
    comando = [python_ejecutable, SCRIPT_TRADUCIR] + sys.argv[1:]
    resultado = subprocess.run(comando)
    sys.exit(resultado.returncode)