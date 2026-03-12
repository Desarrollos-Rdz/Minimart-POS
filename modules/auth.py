import streamlit as st
import hashlib
from utils.db import leer_json, escribir_json, generar_id, fecha_hoy

def hash_password(password: str) -> str:
    """Hashea una contraseña con SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(usuario: str, password: str) -> dict | None:
    """Verifica credenciales y retorna el usuario si son correctas."""
    datos = leer_json("usuarios.json")
    usuarios = datos.get("usuarios", [])
    
    for u in usuarios:
        if u["usuario"] == usuario and u["activo"]:
            # Soporte para passwords sin hash (primera vez) y con hash
            pwd_match = (
                u["password"] == password or
                u["password"] == hash_password(password)
            )
            if pwd_match:
                return u
    return None

def obtener_permisos(rol: str) -> dict:
    """Retorna los permisos de un rol."""
    datos = leer_json("usuarios.json")
    return datos.get("permisos_por_rol", {}).get(rol, {})

def tiene_permiso(permiso: str) -> bool:
    """Verifica si el usuario en sesión tiene un permiso específico."""
    if "usuario" not in st.session_state:
        return False
    permisos = st.session_state.get("permisos", {})
    return permisos.get(permiso, False)

def iniciar_sesion(usuario: dict):
    """Guarda el usuario en session_state."""
    st.session_state["usuario"] = usuario
    st.session_state["permisos"] = obtener_permisos(usuario["rol"])
    st.session_state["autenticado"] = True

def cerrar_sesion():
    """Limpia la sesión."""
    for key in ["usuario", "permisos", "autenticado", "pagina_actual"]:
        if key in st.session_state:
            del st.session_state[key]

def esta_autenticado() -> bool:
    return st.session_state.get("autenticado", False)

def usuario_actual() -> dict:
    return st.session_state.get("usuario", {})

# ── Gestión de usuarios ──────────────────────────────────────────────────────

def crear_usuario(nombre, usuario, password, rol) -> tuple[bool, str]:
    datos = leer_json("usuarios.json")
    usuarios = datos.get("usuarios", [])
    
    # Verificar duplicado
    if any(u["usuario"] == usuario for u in usuarios):
        return False, "El nombre de usuario ya existe."
    
    nuevo = {
        "id": generar_id("u"),
        "nombre": nombre,
        "usuario": usuario,
        "password": hash_password(password),
        "rol": rol,
        "activo": True,
        "fecha_creacion": fecha_hoy(),
        "permisos": datos.get("permisos_por_rol", {}).get(rol, {})
    }
    usuarios.append(nuevo)
    datos["usuarios"] = usuarios
    
    if escribir_json("usuarios.json", datos):
        return True, "Usuario creado correctamente."
    return False, "Error al guardar el usuario."

def actualizar_usuario(user_id, campos: dict) -> tuple[bool, str]:
    datos = leer_json("usuarios.json")
    usuarios = datos.get("usuarios", [])
    
    for i, u in enumerate(usuarios):
        if u["id"] == user_id:
            usuarios[i].update(campos)
            if "rol" in campos:
                usuarios[i]["permisos"] = datos.get("permisos_por_rol", {}).get(campos["rol"], {})
            datos["usuarios"] = usuarios
            if escribir_json("usuarios.json", datos):
                return True, "Usuario actualizado."
            return False, "Error al guardar."
    return False, "Usuario no encontrado."

def cambiar_password(user_id, nueva_password) -> tuple[bool, str]:
    return actualizar_usuario(user_id, {"password": hash_password(nueva_password)})

def listar_usuarios() -> list:
    datos = leer_json("usuarios.json")
    return datos.get("usuarios", [])

def obtener_roles() -> dict:
    datos = leer_json("usuarios.json")
    return datos.get("roles", {})