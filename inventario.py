from utils.db import leer_json, escribir_json, generar_id, fecha_hoy

def listar_productos(seccion: str = None, activos_only: bool = True) -> list:
    datos = leer_json("productos.json")
    productos = datos.get("productos", [])
    if activos_only:
        productos = [p for p in productos if p.get("activo", True)]
    if seccion:
        productos = [p for p in productos if p.get("seccion") == seccion]
    return productos

def buscar_producto(termino: str) -> list:
    """Busca por nombre, código o categoría."""
    productos = listar_productos()
    termino = termino.lower()
    return [
        p for p in productos
        if termino in p["nombre"].lower()
        or termino in p.get("codigo", "").lower()
        or termino in p.get("categoria", "").lower()
    ]

def obtener_producto(producto_id: str) -> dict | None:
    datos = leer_json("productos.json")
    for p in datos.get("productos", []):
        if p["id"] == producto_id:
            return p
    return None

def obtener_producto_por_codigo(codigo: str) -> dict | None:
    datos = leer_json("productos.json")
    for p in datos.get("productos", []):
        if p.get("codigo") == codigo and p.get("activo", True):
            return p
    return None

def agregar_producto(datos_producto: dict) -> tuple[bool, str]:
    datos = leer_json("productos.json")
    productos = datos.get("productos", [])
    
    nuevo = {
        "id": generar_id("p"),
        "fecha_alta": fecha_hoy(),
        "activo": True,
        **datos_producto
    }
    productos.append(nuevo)
    datos["productos"] = productos
    
    if escribir_json("productos.json", datos):
        return True, f"Producto '{nuevo['nombre']}' agregado correctamente."
    return False, "Error al guardar el producto."

def actualizar_producto(producto_id: str, campos: dict) -> tuple[bool, str]:
    datos = leer_json("productos.json")
    productos = datos.get("productos", [])
    
    for i, p in enumerate(productos):
        if p["id"] == producto_id:
            productos[i].update(campos)
            datos["productos"] = productos
            if escribir_json("productos.json", datos):
                return True, "Producto actualizado."
            return False, "Error al guardar."
    return False, "Producto no encontrado."

def eliminar_producto(producto_id: str) -> tuple[bool, str]:
    """Desactiva el producto (no lo borra físicamente)."""
    return actualizar_producto(producto_id, {"activo": False})

def actualizar_stock(producto_id: str, cantidad: int, operacion: str = "restar") -> tuple[bool, str]:
    """
    Actualiza el stock de un producto.
    operacion: 'restar' para ventas, 'sumar' para entradas
    """
    producto = obtener_producto(producto_id)
    if not producto:
        return False, "Producto no encontrado."
    
    stock_actual = producto.get("stock", 0)
    
    if operacion == "restar":
        if stock_actual < cantidad:
            return False, f"Stock insuficiente. Disponible: {stock_actual}"
        nuevo_stock = stock_actual - cantidad
    else:
        nuevo_stock = stock_actual + cantidad
    
    return actualizar_producto(producto_id, {"stock": nuevo_stock})

def productos_bajo_stock() -> list:
    """Retorna productos con stock menor al mínimo."""
    productos = listar_productos()
    return [
        p for p in productos
        if p.get("stock", 0) <= p.get("stock_minimo", 0)
    ]

def obtener_categorias() -> dict:
    datos = leer_json("productos.json")
    return datos.get("categorias", {})
