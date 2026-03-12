from utils.db import leer_json, escribir_json, generar_id, fecha_hoy, hora_ahora

def registrar_recarga(telefono: str, operadora: str, monto: float, usuario_id: str) -> tuple[bool, str]:
    datos = leer_json("recargas.json")
    recargas = datos.get("recargas", [])
    
    nueva = {
        "id": generar_id("r"),
        "fecha": fecha_hoy(),
        "hora": hora_ahora(),
        "telefono": telefono,
        "operadora": operadora,
        "monto": monto,
        "usuario_id": usuario_id
    }
    recargas.append(nueva)
    datos["recargas"] = recargas
    
    if escribir_json("recargas.json", datos):
        return True, f"Recarga de ${monto:.2f} registrada para {telefono} ({operadora})."
    return False, "Error al registrar la recarga."

def recargas_del_dia(fecha: str = None) -> list:
    if not fecha:
        fecha = fecha_hoy()
    datos = leer_json("recargas.json")
    return [r for r in datos.get("recargas", []) if r["fecha"] == fecha]

def historial_recargas(fecha_inicio: str = None, fecha_fin: str = None) -> list:
    datos = leer_json("recargas.json")
    recargas = datos.get("recargas", [])
    if fecha_inicio:
        recargas = [r for r in recargas if r["fecha"] >= fecha_inicio]
    if fecha_fin:
        recargas = [r for r in recargas if r["fecha"] <= fecha_fin]
    return sorted(recargas, key=lambda x: (x["fecha"], x["hora"]), reverse=True)

def obtener_operadoras() -> list:
    datos = leer_json("recargas.json")
    return datos.get("operadoras", [])
