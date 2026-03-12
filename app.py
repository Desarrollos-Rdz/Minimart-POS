import streamlit as st
from modules.auth import verificar_login, iniciar_sesion, cerrar_sesion, esta_autenticado, usuario_actual, tiene_permiso
from utils.db import leer_json

st.set_page_config(
    page_title="Minimart POS",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Estilos globales ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Ocultar sidebar y hamburguesa */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Barra de navegación superior */
[data-testid="stHeader"] {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%) !important;
}
[data-testid="stHeader"] * { color: white !important; }

/* Tabs de navegación */
[data-testid="stNavigation"] {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    padding: 0 1rem;
    border-bottom: 2px solid rgba(233,69,96,0.4);
}
[data-testid="stNavigation"] a {
    color: rgba(255,255,255,0.75) !important;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 0.75rem 1rem !important;
    border-radius: 0 !important;
    transition: all 0.2s;
}
[data-testid="stNavigation"] a:hover {
    color: white !important;
    background: rgba(233,69,96,0.15) !important;
}
[data-testid="stNavigation"] a[aria-selected="true"] {
    color: white !important;
    border-bottom: 3px solid #e94560 !important;
    background: rgba(233,69,96,0.1) !important;
}

/* Métricas */
[data-testid="stMetric"] {
    background: white;
    border-radius: 12px;
    padding: 1.2rem;
    border: 1px solid #f0f0f0;
    border-left: 4px solid #e94560;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="stMetricValue"] { font-weight: 700; color: #1a1a2e !important; }

/* Botón primario */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #e94560, #c23152) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #c23152, #a0223e) !important;
    box-shadow: 0 4px 12px rgba(233,69,96,0.35) !important;
}

/* Cards generales */
.pos-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border: 1px solid #f0f0f0;
    margin-bottom: 1rem;
}
.stock-alert {
    background: #fff8e1;
    border-left: 4px solid #ffc107;
    padding: 0.6rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.35rem 0;
    font-size: 0.92rem;
}
.page-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    color: white;
    padding: 1.25rem 1.75rem;
    border-radius: 14px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ── Pantalla de login ─────────────────────────────────────────────────────────
def pantalla_login():
    config = leer_json("config_tienda.json")
    nombre_tienda = config.get("tienda", {}).get("nombre", "Minimart POS")

    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:2rem;">
            <div style="font-size:3.5rem;">🛒</div>
            <h1 style="color:#1a1a2e; font-weight:800; margin:0.25rem 0 0;">{nombre_tienda}</h1>
            <p style="color:#888; margin:0.25rem 0 0; font-size:0.95rem;">Sistema de Punto de Venta</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login", border=False):
            st.markdown('<div class="pos-card">', unsafe_allow_html=True)
            usuario = st.text_input("👤 Usuario", placeholder="Tu usuario")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Tu contraseña")
            submitted = st.form_submit_button("Iniciar sesión", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

            if submitted:
                if not usuario or not password:
                    st.error("Ingresa usuario y contraseña.")
                else:
                    u = verificar_login(usuario, password)
                    if u:
                        iniciar_sesion(u)
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")

        st.markdown("""
        <p style="text-align:center; color:#bbb; font-size:0.78rem; margin-top:1.5rem;">
            Minimart POS v1.0.0
        </p>""", unsafe_allow_html=True)


# ── Barra superior con info de usuario ───────────────────────────────────────
def barra_usuario():
    u = usuario_actual()
    color_rol = {"admin": "#e94560", "supervisor": "#F0A500",
                 "cajero": "#00B4D8", "almacenista": "#4CAF50"}.get(u.get("rol", ""), "#aaa")

    col_logo, col_spacer, col_user = st.columns([2, 6, 2])
    with col_logo:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.5rem; padding:0.5rem 0;">
            <span style="font-size:1.6rem;">🛒</span>
            <span style="font-weight:800; font-size:1rem; color:#1a1a2e;">Minimart POS</span>
        </div>""", unsafe_allow_html=True)
    with col_user:
        st.markdown(f"""
        <div style="text-align:right; padding:0.4rem 0; line-height:1.3;">
            <span style="font-weight:600; font-size:0.9rem; color:#1a1a2e;">{u.get('nombre','')}</span><br>
            <span style="font-size:0.75rem; color:{color_rol}; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">{u.get('rol','')}</span>
        </div>""", unsafe_allow_html=True)

    if st.button("🚪 Salir", key="btn_logout"):
        cerrar_sesion()
        st.rerun()
    st.divider()


# ── Construcción dinámica de páginas según rol ────────────────────────────────
def construir_navegacion():
    secciones = {}

    # Principal
    principal = []
    if tiene_permiso("ver_dashboard"):
        principal.append(st.Page("pages/dashboard.py", title="🏠 Dashboard", default=True))
    if tiene_permiso("hacer_ventas"):
        principal.append(st.Page("pages/pos.py", title="🛒 Punto de Venta",
                                  default=(not tiene_permiso("ver_dashboard"))))
    if principal:
        secciones["Principal"] = principal

    # Operaciones
    operaciones = []
    if tiene_permiso("ver_inventario"):
        operaciones.append(st.Page("pages/inventario.py", title="📦 Inventario"))
    if tiene_permiso("hacer_recargas"):
        operaciones.append(st.Page("pages/recargas.py", title="📱 Recargas"))
    if tiene_permiso("ver_caja"):
        operaciones.append(st.Page("pages/caja.py", title="💰 Caja"))
    if operaciones:
        secciones["Operaciones"] = operaciones

    # Administración
    admin_pages = []
    if tiene_permiso("gestionar_usuarios"):
        admin_pages.append(st.Page("pages/usuarios.py", title="👥 Usuarios"))
    if tiene_permiso("configuracion"):
        admin_pages.append(st.Page("pages/configuracion.py", title="⚙️ Configuración"))
    if admin_pages:
        secciones["Administración"] = admin_pages

    return secciones


# ── Main ──────────────────────────────────────────────────────────────────────
if not esta_autenticado():
    pantalla_login()
else:
    barra_usuario()
    nav = construir_navegacion()
    if nav:
        pg = st.navigation(nav, position="top")
        pg.run()
    else:
        st.error("Tu usuario no tiene permisos asignados. Contacta al administrador.")