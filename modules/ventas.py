from utils.db import leer_json, escribir_json, generar_id, fecha_hoy, hora_ahora
from modules.inventario import actualizar_stock, obtener_producto

def registrar_venta(items: list, metodo_pago: str, usuario_id: str,
                    monto_recibido: float = 0.0, descuento: float = 0.0) -> tuple[bool, str, dict]:
    """
    Registra una venta completa.
    items: [{"producto_id": ..., "nombre": ..., "cantidad": ..., "precio_unitario": ..., "subtotal": ...}]
    metodo_pago: 'efectivo' | 'tarjeta' | 'mixto'
    """
    if not items:
        return False, "No hay productos en la venta.", {}

    subtotal = sum(i["subtotal"] for i in items)
    total = subtotal - descuento
    cambio = monto_recibido - total if metodo_pago == "efectivo" else 0.0

    venta = {
        "id": generar_id("v"),
        "fecha": fecha_hoy(),
        "hora": hora_ahora(),
        "items": items,
        "subtotal": subtotal,
        "descuento": descuento,
        "total": total,
        "metodo_pago": metodo_pago,
        "monto_recibido": monto_recibido,
        "cambio": cambio,
        "usuario_id": usuario_id,
        "cancelada": False
    }

    # Descontar stock
    for item in items:
        ok, msg = actualizar_stock(item["producto_id"], item["cantidad"], "restar")
        if not ok:
            return False, f"Error de stock en '{item['nombre']}': {msg}", {}

    # Guardar venta
    datos = leer_json("ventas.json")
    ventas = datos.get("ventas", [])
    ventas.append(venta)
    datos["ventas"] = ventas

    if escribir_json("ventas.json", datos):
        return True, "Venta registrada correctamente.", venta
    return False, "Error al guardar la venta.", {}

def cancelar_venta(venta_id: str, usuario_id: str) -> tuple[bool, str]:
    """Cancela una venta y devuelve el stock."""
    datos = leer_json("ventas.json")
    ventas = datos.get("ventas", [])

    for i, v in enumerate(ventas):
        if v["id"] == venta_id:
            if v.get("cancelada"):
                return False, "La venta ya fue cancelada."
            ventas[i]["cancelada"] = True
            ventas[i]["cancelada_por"] = usuario_id
            ventas[i]["hora_cancelacion"] = hora_ahora()

            # Devolver stock
            for item in v["items"]:
                actualizar_stock(item["producto_id"], item["cantidad"], "sumar")

            datos["ventas"] = ventas
            if escribir_json("ventas.json", datos):
                return True, "Venta cancelada y stock restaurado."
            return False, "Error al cancelar."
    return False, "Venta no encontrada."

def ventas_del_dia(fecha: str = None) -> list:
    if not fecha:
        fecha = fecha_hoy()
    datos = leer_json("ventas.json")
    return [
        v for v in datos.get("ventas", [])
        if v["fecha"] == fecha and not v.get("cancelada")
    ]

def resumen_del_dia(fecha: str = None) -> dict:
    ventas = ventas_del_dia(fecha)
    total_ventas = sum(v["total"] for v in ventas)
    total_efectivo = sum(v["total"] for v in ventas if v["metodo_pago"] == "efectivo")
    total_tarjeta = sum(v["total"] for v in ventas if v["metodo_pago"] == "tarjeta")
    total_mixto = sum(v["total"] for v in ventas if v["metodo_pago"] == "mixto")
    
    # Costo total (para calcular utilidad)
    costo_total = 0
    for v in ventas:
        for item in v["items"]:
            producto = obtener_producto(item["producto_id"])
            if producto:
                costo_total += producto.get("precio_compra", 0) * item["cantidad"]

    return {
        "total_ventas": len(ventas),
        "ingresos_totales": total_ventas,
        "efectivo": total_efectivo,
        "tarjeta": total_tarjeta,
        "mixto": total_mixto,
        "costo_total": costo_total,
        "utilidad": total_ventas - costo_total
    }

def historial_ventas(fecha_inicio: str = None, fecha_fin: str = None) -> list:
    datos = leer_json("ventas.json")
    ventas = [v for v in datos.get("ventas", []) if not v.get("cancelada")]
    
    if fecha_inicio:
        ventas = [v for v in ventas if v["fecha"] >= fecha_inicio]
    if fecha_fin:
        ventas = [v for v in ventas if v["fecha"] <= fecha_fin]
    
    return sorted(ventas, key=lambda x: (x["fecha"], x["hora"]), reverse=True)