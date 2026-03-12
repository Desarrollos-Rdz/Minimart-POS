import streamlit as st
from modules.auth import (crear_usuario, listar_usuarios, actualizar_usuario,
                           cambiar_password, obtener_roles, usuario_actual)
from utils.db import formato_moneda

st.markdown("""
<div class="page-header">
    <span style="font-size:2rem;">👥</span>
    <div>
        <h2 style="margin:0; color:white; font-weight:700;">Gestión de Usuarios</h2>
        <p style="margin:0; opacity:0.75; font-size:0.88rem;">Administra accesos y roles del sistema</p>
    </div>
</div>
""", unsafe_allow_html=True)

roles = obtener_roles()
tab_lista, tab_nuevo, tab_roles = st.tabs(["👥 Usuarios", "➕ Nuevo usuario", "🏷️ Info de roles"])

# ── Lista de usuarios ─────────────────────────────────────────────────────────
with tab_lista:
    usuarios = listar_usuarios()
    u_actual = usuario_actual()

    activos   = [u for u in usuarios if u.get("activo")]
    inactivos = [u for u in usuarios if not u.get("activo")]

    st.caption(f"{len(activos)} usuarios activos · {len(inactivos)} inactivos")

    for u in usuarios:
        rol_info = roles.get(u["rol"], {})
        color = rol_info.get("color", "#aaa")
        es_yo = u["id"] == u_actual["id"]

        with st.container():
            ca, cb, cc, cd = st.columns([2, 1.5, 1, 1.2])
            with ca:
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <div style="width:38px; height:38px; border-radius:50%; background:{color}22;
                                border:2px solid {color}; display:flex; align-items:center;
                                justify-content:center; font-weight:700; color:{color}; font-size:1rem;">
                        {u['nombre'][0].upper()}
                    </div>
                    <div>
                        <div style="font-weight:600;">{u['nombre']} {"<span style='font-size:0.75rem; background:#e3f2fd; color:#1565c0; padding:1px 6px; border-radius:4px;'>Tú</span>" if es_yo else ""}</div>
                        <div style="color:#888; font-size:0.85rem;">@{u['usuario']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with cb:
                st.markdown(f"<span style='color:{color}; font-weight:600;'>● {rol_info.get('nombre', u['rol'])}</span>", unsafe_allow_html=True)
                st.caption(rol_info.get("descripcion", ""))
            with cc:
                if u.get("activo"):
                    st.markdown("🟢 **Activo**")
                else:
                    st.markdown("🔴 Inactivo")
                st.caption(f"Alta: {u.get('fecha_creacion', '—')}")
            with cd:
                if not es_yo:
                    nuevo_estado = not u.get("activo", True)
                    label = "🚫 Desactivar" if u.get("activo") else "✅ Activar"
                    if st.button(label, key=f"tog_{u['id']}", use_container_width=True):
                        actualizar_usuario(u["id"], {"activo": nuevo_estado})
                        st.rerun()

                    if st.button("🔑 Cambiar pass", key=f"chp_{u['id']}", use_container_width=True):
                        st.session_state[f"chp_{u['id']}"] = not st.session_state.get(f"chp_{u['id']}", False)
                        st.rerun()

            # Cambiar contraseña inline
            if st.session_state.get(f"chp_{u['id']}", False):
                with st.form(f"f_chp_{u['id']}"):
                    nueva_pass = st.text_input("Nueva contraseña", type="password", min_chars=6)
                    confirmar  = st.text_input("Confirmar contraseña", type="password")
                    c_ok, c_x  = st.columns(2)
                    if c_ok.form_submit_button("💾 Guardar", type="primary"):
                        if nueva_pass != confirmar:
                            st.error("Las contraseñas no coinciden.")
                        elif len(nueva_pass) < 6:
                            st.error("Mínimo 6 caracteres.")
                        else:
                            ok, msg = cambiar_password(u["id"], nueva_pass)
                            st.success(msg) if ok else st.error(msg)
                            if ok:
                                st.session_state[f"chp_{u['id']}"] = False
                                st.rerun()
                    if c_x.form_submit_button("❌ Cancelar"):
                        st.session_state[f"chp_{u['id']}"] = False
                        st.rerun()

        st.divider()

# ── Nuevo usuario ─────────────────────────────────────────────────────────────
with tab_nuevo:
    with st.form("form_nuevo_user", border=False):
        st.markdown('<div class="pos-card">', unsafe_allow_html=True)
        st.subheader("Datos del nuevo usuario")

        c1, c2 = st.columns(2)
        nombre   = c1.text_input("Nombre completo *")
        usuario_n = c2.text_input("Usuario para login *", help="Sin espacios ni caracteres especiales")

        c3, c4 = st.columns(2)
        password  = c3.text_input("Contraseña *", type="password")
        confirmar = c4.text_input("Confirmar contraseña *", type="password")

        rol = st.selectbox("Rol *", list(roles.keys()),
                            format_func=lambda r: f"{roles[r]['nombre']} — {roles[r]['descripcion']}")

        # Vista previa de permisos
        if rol:
            ri = roles[rol]
            st.markdown(f"""
            <div style="background:{ri.get('color','#aaa')}11; border-left:4px solid {ri.get('color','#aaa')};
                        padding:0.75rem 1rem; border-radius:0 8px 8px 0; margin:0.5rem 0;">
                <strong style="color:{ri.get('color','#aaa')};">{ri['nombre']}</strong><br>
                <span style="font-size:0.9rem; color:#555;">{ri['descripcion']}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if st.form_submit_button("➕ Crear usuario", type="primary", use_container_width=True):
            if not nombre or not usuario_n or not password:
                st.error("Todos los campos con * son obligatorios.")
            elif password != confirmar:
                st.error("Las contraseñas no coinciden.")
            elif len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            else:
                ok, msg = crear_usuario(nombre, usuario_n, password, rol)
                st.success(msg) if ok else st.error(msg)
                if ok:
                    st.rerun()

# ── Info de roles ─────────────────────────────────────────────────────────────
with tab_roles:
    st.subheader("Descripción de roles y permisos")
    from utils.db import leer_json
    datos = leer_json("usuarios.json")
    permisos_por_rol = datos.get("permisos_por_rol", {})

    permisos_labels = {
        "ver_dashboard": "Ver Dashboard",
        "ver_ventas": "Ver Ventas",
        "hacer_ventas": "Hacer Ventas",
        "ver_inventario": "Ver Inventario",
        "editar_inventario": "Editar Inventario",
        "ver_caja": "Ver Caja",
        "hacer_corte": "Hacer Corte",
        "ver_recargas": "Ver Recargas",
        "hacer_recargas": "Hacer Recargas",
        "ver_usuarios": "Ver Usuarios",
        "gestionar_usuarios": "Gestionar Usuarios",
        "ver_reportes": "Ver Reportes",
        "configuracion": "Configuración",
    }

    cols = st.columns(len(roles))
    for i, (rol_key, rol_info) in enumerate(roles.items()):
        with cols[i]:
            color = rol_info.get("color", "#aaa")
            st.markdown(f"""
            <div style="background:{color}15; border:2px solid {color}; border-radius:12px; padding:1rem; text-align:center; margin-bottom:1rem;">
                <div style="font-weight:700; color:{color}; font-size:1rem;">{rol_info['nombre']}</div>
                <div style="font-size:0.78rem; color:#666; margin-top:0.25rem;">{rol_info['descripcion']}</div>
            </div>
            """, unsafe_allow_html=True)

            perms = permisos_por_rol.get(rol_key, {})
            for perm_key, perm_label in permisos_labels.items():
                tiene = perms.get(perm_key, False)
                st.markdown(f"{'✅' if tiene else '⛔'} {perm_label}")