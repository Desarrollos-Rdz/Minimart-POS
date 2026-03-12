import json
import os
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def leer_json(archivo: str) -> dict:
    """Lee un archivo JSON y retorna su contenido."""
    ruta = os.path.join(DATA_PATH, archivo)
    if not os.path.exists(ruta):
        return {}
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def escribir_json(archivo: str, datos: dict) -> bool:
    """Escribe datos en un archivo JSON."""
    ruta = os.path.join(DATA_PATH, archivo)
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error al escribir {archivo}: {e}")
        return False

def generar_id(prefijo: str = "") -> str:
    """Genera un ID único basado en timestamp."""
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"{prefijo}{ts}"

def fecha_hoy() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def hora_ahora() -> str:
    return datetime.now().strftime("%H:%M:%S")

def formato_moneda(valor: float) -> str:
    return f"${valor:,.2f}"