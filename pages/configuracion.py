import streamlit as st
from utils.db import leer_json, escribir_json

st.markdown("""
<div class="page-header">
    <span style="font-size:2rem;">⚙️</span>
    <div>
        <h2 style="margin:0; color:white; font-weight:700;">Configuración</h2>
        <p style="margin:0; opacity:0.75; font-size:0.88rem;">Ajustes generales de la tienda</p>
    </div>
</div>
""", unsafe_allow_html=True)

config = leer_json("config_tienda.json")
tienda = config.get("tienda", {})
sistema = config.get("sistema", {})

tab_tienda, tab_sistema = st.tabs(["🏪 Datos de la tienda", "ℹ️ Sistema"])

with tab_tienda:
    with st.form("form_config_tienda", border=False):
        st.markdown('<div class="pos-card">', unsafe_allow_html=True)
        st.subheader("Información de la tienda")

        c1, c2 = st.columns(2)
        nombre   = c1.text_input("🏪 Nombre de la tienda", value=tienda.get("nombre", ""))
        slogan   = c2.text_input("💬 Slogan", value=tienda.get("slogan", ""))
        direccion = c1.text_input("📍 Dirección", value=tienda.get("direccion", ""))
        telefono  = c2.text_input("📞 Teléfono", value=tienda.get("telefono", ""))
        ticket_pie = st.text_area("🧾 Mensaje en ticket de venta",
                                   value=tienda.get("ticket_pie", "¡Gracias por su compra!"),
                                   help="Este texto aparecerá al final del ticket de venta")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.form_submit_button("💾 Guardar configuración", type="primary", use_container_width=True):
            config["tienda"].update({
                "nombre": nombre, "slogan": slogan,
                "direccion": direccion, "telefono": telefono,
                "ticket_pie": ticket_pie
            })
            if escribir_json("config_tienda.json", config):
                st.success("✅ Configuración guardada correctamente.")
                st.rerun()
            else:
                st.error("Error al guardar la configuración.")

with tab_sistema:
    st.markdown('<div class="pos-card">', unsafe_allow_html=True)
    st.subheader("Información del sistema")
    c1, c2 = st.columns(2)
    c1.write(f"**Versión:** {sistema.get('version', '1.0.0')}")
    c2.write(f"**Instalación:** {sistema.get('fecha_instalacion', '—')}")
    c1.write(f"**Idioma:** {sistema.get('idioma', 'es').upper()}")
    c2.write(f"**Moneda:** {config.get('tienda', {}).get('moneda', 'MXN')}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔑 Cambiar mi contraseña")
    from modules.auth import usuario_actual, cambiar_password
    with st.form("form_mi_pass", border=False):
        st.markdown('<div class="pos-card">', unsafe_allow_html=True)
        pass_actual  = st.text_input("Contraseña actual", type="password")
        pass_nueva   = st.text_input("Nueva contraseña", type="password")
        pass_confirm = st.text_input("Confirmar nueva contraseña", type="password")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.form_submit_button("🔑 Cambiar contraseña", type="primary"):
            from modules.auth import verificar_login
            u = usuario_actual()
            verificado = verificar_login(u["usuario"], pass_actual)
            if not verificado:
                st.error("La contraseña actual es incorrecta.")
            elif pass_nueva != pass_confirm:
                st.error("Las contraseñas nuevas no coinciden.")
            elif len(pass_nueva) < 6:
                st.error("La nueva contraseña debe tener al menos 6 caracteres.")
            else:
                ok, msg = cambiar_password(u["id"], pass_nueva)
                st.success(msg) if ok else st.error(msg)