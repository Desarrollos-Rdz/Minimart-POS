from utils.db import leer_json, escribir_json, generar_id, fecha_hoy, hora_ahora
from modules.ventas import resumen_del_dia
from modules.recargas import recargas_del_dia

def abrir_caja(fondo_inicial: float, usuario_id: str) -> tuple[bool, str]:
    datos = leer_json("caja.json")
    caja = datos.get("caja_actual", {})
    
    if caja.get("abierta"):
        return False, "La caja ya está abierta."
    
    datos["caja_actual"] = {
        "fondo_inicial": fondo_inicial,
        "fecha_apertura": fecha_hoy(),
        "hora_apertura": hora_ahora(),
        "abierta": True,
        "usuario_apertura": usuario_id
    }
    
    if escribir_json("caja.json", datos):
        return True, f"Caja abierta con fondo de ${fondo_inicial:.2f}"
    return False, "Error al abrir caja."

def hacer_corte(usuario_id: str, efectivo_contado: float, notas: str = "") -> tuple[bool, str, dict]:
    datos = leer_json("caja.json")
    caja = datos.get("caja_actual", {})
    
    if not caja.get("abierta"):
        return False, "La caja no está abierta.", {}
    
    resumen = resumen_del_dia()
    recargas = recargas_del_dia()
    total_recargas = sum(r["monto"] for r in recargas)
    
    efectivo_esperado = caja.get("fondo_inicial", 0) + resumen["efectivo"] + total_recargas
    diferencia = efectivo_contado - efectivo_esperado

    corte = {
        "id": generar_id("c"),
        "fecha": fecha_hoy(),
        "hora_corte": hora_ahora(),
        "usuario_id": usuario_id,
        "fondo_inicial": caja.get("fondo_inicial", 0),
        "ventas_totales": resumen["ingresos_totales"],
        "ventas_efectivo": resumen["efectivo"],
        "ventas_tarjeta": resumen["tarjeta"],
        "ventas_mixto": resumen["mixto"],
        "num_ventas": resumen["total_ventas"],
        "total_recargas": total_recargas,
        "costo_total": resumen["costo_total"],
        "utilidad_ventas": resumen["utilidad"],
        "efectivo_esperado": efectivo_esperado,
        "efectivo_contado": efectivo_contado,
        "diferencia": diferencia,
        "notas": notas
    }

    # Guardar corte y cerrar caja
    cortes = datos.get("cortes", [])
    cortes.append(corte)
    datos["cortes"] = cortes
    datos["caja_actual"] = {"abierta": False, "fondo_inicial": 0, "fecha_apertura": None, "usuario_apertura": None}

    if escribir_json("caja.json", datos):
        return True, "Corte realizado correctamente.", corte
    return False, "Error al guardar el corte.", {}

def estado_caja() -> dict:
    datos = leer_json("caja.json")
    return datos.get("caja_actual", {"abierta": False})

def historial_cortes() -> list:
    datos = leer_json("caja.json")
    return sorted(datos.get("cortes", []), key=lambda x: x["fecha"], reverse=True)