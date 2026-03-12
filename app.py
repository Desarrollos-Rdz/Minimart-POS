import streamlit as st
from modules.auth import (
    verificar_login, iniciar_sesion, cerrar_sesion,
    esta_autenticado, usuario_actual, tiene_permiso
)
from utils.db import leer_json

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_name="Minimart POS",
    page_title="Minimart POS",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Estilos globales ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fuente principal */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    /* Botones primarios */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e94560, #c23152);
        border: none;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
    }
    
    /* Métricas */
    [data-testid="stMetric"] {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid #e94560;
    }
    
    /* Header de la app */
    .app-header {
        background: linear-gradient(135deg, #1a1a2e, #0f3460);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }
    
    /* Alerta de stock bajo */
    .stock-alert {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Pantalla de Login ────────────────────────────────────────────────────────
def pantalla_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        config = leer_json("config_tienda.json")
        nombre_tienda = config.get("tienda", {}).get("nombre", "Minimart POS")
        
        st.markdown(f"""
        <div style="text-align:center; margin-bottom: 2rem;">
            <div style="font-size: 3.5rem;">🛒</div>
            <h1 style="color: #1a1a2e; font-weight: 700; margin: 0;">{nombre_tienda}</h1>
            <p style="color: #666; margin-top: 0.25rem;">Sistema de Punto de Venta</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
            submitted = st.form_submit_button("Iniciar Sesión", use_container_width=True, type="primary")

            if submitted:
                if not usuario or not password:
                    st.error("Por favor ingresa usuario y contraseña.")
                else:
                    u = verificar_login(usuario, password)
                    if u:
                        iniciar_sesion(u)
                        st.success(f"¡Bienvenido, {u['nombre']}!")
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")
        
        st.markdown("""
        <p style="text-align:center; color:#aaa; font-size:0.8rem; margin-top:2rem;">
            v1.0.0 · Minimart POS
        </p>
        """, unsafe_allow_html=True)


# ── Sidebar de navegación ────────────────────────────────────────────────────
def sidebar_navegacion():
    u = usuario_actual()
    config = leer_json("config_tienda.json")
    nombre_tienda = config.get("tienda", {}).get("nombre", "Minimart POS")
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding: 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 2rem;">🛒</div>
            <div style="font-weight: 700; font-size: 1.1rem;">{nombre_tienda}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Info usuario
        color_rol = {"admin": "#e94560", "supervisor": "#F0A500", "cajero": "#00B4D8", "almacenista": "#4CAF50"}.get(u.get("rol"), "#aaa")
        st.markdown(f"""
        <div style="padding: 0.75rem; margin: 1rem 0; background: rgba(255,255,255,0.05); border-radius: 8px; border-left: 3px solid {color_rol};">
            <div style="font-weight: 600;">{u.get('nombre', 'Usuario')}</div>
            <div style="font-size: 0.8rem; color: {color_rol}; text-transform: uppercase; letter-spacing: 1px;">{u.get('rol', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Menú según permisos
        pagina = None
        
        if tiene_permiso("ver_dashboard") or tiene_permiso("hacer_ventas"):
            st.markdown("**📊 Principal**")
        
        if tiene_permiso("ver_dashboard"):
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state["pagina_actual"] = "dashboard"
        
        if tiene_permiso("hacer_ventas"):
            if st.button("🛒 Punto de Venta", use_container_width=True):
                st.session_state["pagina_actual"] = "pos"
        
        if tiene_permiso("ver_inventario"):
            st.markdown("**📦 Inventario**")
            if st.button("📦 Inventario", use_container_width=True):
                st.session_state["pagina_actual"] = "inventario"
        
        if tiene_permiso("ver_caja"):
            st.markdown("**💰 Caja**")
            if st.button("💰 Caja y Cortes", use_container_width=True):
                st.session_state["pagina_actual"] = "caja"
        
        if tiene_permiso("hacer_recargas"):
            if st.button("📱 Recargas", use_container_width=True):
                st.session_state["pagina_actual"] = "recargas"
        
        if tiene_permiso("gestionar_usuarios"):
            st.markdown("**⚙️ Administración**")
            if st.button("👥 Usuarios", use_container_width=True):
                st.session_state["pagina_actual"] = "usuarios"
            if st.button("⚙️ Configuración", use_container_width=True):
                st.session_state["pagina_actual"] = "configuracion"
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            cerrar_sesion()
            st.rerun()


# ── Páginas ──────────────────────────────────────────────────────────────────
def pagina_dashboard():
    from modules.ventas import resumen_del_dia, historial_ventas
    from modules.inventario import productos_bajo_stock
    from utils.db import formato_moneda, fecha_hoy
    
    st.markdown("""
    <div class="app-header">
        <span style="font-size:1.8rem">🏠</span>
        <div>
            <h2 style="margin:0; color:white">Dashboard</h2>
            <p style="margin:0; opacity:0.7; font-size:0.9rem">Resumen del día</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    resumen = resumen_del_dia()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Ingresos del día", formato_moneda(resumen["ingresos_totales"]))
    with col2:
        st.metric("📈 Utilidad estimada", formato_moneda(resumen["utilidad"]))
    with col3:
        st.metric("🛒 Ventas realizadas", resumen["total_ventas"])
    with col4:
        alertas = len(productos_bajo_stock())
        st.metric("⚠️ Alertas de stock", alertas, delta=f"-{alertas}" if alertas > 0 else None)
    
    st.markdown("---")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("💳 Desglose por método de pago")
        metodos = {
            "💵 Efectivo": resumen["efectivo"],
            "💳 Tarjeta": resumen["tarjeta"],
            "🔀 Mixto": resumen["mixto"]
        }
        for m, v in metodos.items():
            st.write(f"{m}: **{formato_moneda(v)}**")
    
    with col_b:
        st.subheader("⚠️ Productos con stock bajo")
        bajos = productos_bajo_stock()
        if bajos:
            for p in bajos[:5]:
                st.markdown(f"""
                <div class="stock-alert">
                    <strong>{p['nombre']}</strong> — Stock: {p['stock']} (mín: {p['stock_minimo']})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Todos los productos tienen stock suficiente.")


def pagina_pos():
    from modules.inventario import buscar_producto, obtener_producto_por_codigo
    from modules.ventas import registrar_venta
    from utils.db import formato_moneda
    
    st.markdown("""
    <div class="app-header">
        <span style="font-size:1.8rem">🛒</span>
        <div>
            <h2 style="margin:0; color:white">Punto de Venta</h2>
            <p style="margin:0; opacity:0.7; font-size:0.9rem">Registra ventas rápidamente</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if "carrito" not in st.session_state:
        st.session_state.carrito = []
    
    col_busqueda, col_carrito = st.columns([1.2, 1])
    
    with col_busqueda:
        st.subheader("🔍 Buscar producto")
        busqueda = st.text_input("Nombre, código o categoría", key="busqueda_pos", placeholder="Ej: Coca Cola, 7501055...")
        
        if busqueda:
            resultados = buscar_producto(busqueda)
            if resultados:
                for p in resultados[:8]:
                    col_info, col_btn = st.columns([3, 1])
                    with col_info:
                        st.write(f"**{p['nombre']}** — {formato_moneda(p['precio_venta'])} | Stock: {p['stock']}")
                    with col_btn:
                        if st.button("➕", key=f"add_{p['id']}", help="Agregar al carrito"):
                            # Verificar si ya está en el carrito
                            en_carrito = False
                            for item in st.session_state.carrito:
                                if item["producto_id"] == p["id"]:
                                    if item["cantidad"] < p["stock"]:
                                        item["cantidad"] += 1
                                        item["subtotal"] = item["cantidad"] * item["precio_unitario"]
                                    else:
                                        st.warning("Stock insuficiente.")
                                    en_carrito = True
                                    break
                            if not en_carrito:
                                if p["stock"] > 0:
                                    st.session_state.carrito.append({
                                        "producto_id": p["id"],
                                        "nombre": p["nombre"],
                                        "cantidad": 1,
                                        "precio_unitario": p["precio_venta"],
                                        "subtotal": p["precio_venta"]
                                    })
                                else:
                                    st.error("Sin stock disponible.")
                            st.rerun()
            else:
                st.info("No se encontraron productos.")
    
    with col_carrito:
        st.subheader(f"🧾 Carrito ({len(st.session_state.carrito)} items)")
        
        if not st.session_state.carrito:
            st.info("El carrito está vacío.")
        else:
            total = 0
            for i, item in enumerate(st.session_state.carrito):
                col_n, col_c, col_x = st.columns([2, 1, 0.5])
                with col_n:
                    st.write(f"**{item['nombre']}**")
                    st.write(f"{formato_moneda(item['precio_unitario'])} × {item['cantidad']} = **{formato_moneda(item['subtotal'])}**")
                with col_c:
                    nueva_cant = st.number_input("Cant.", min_value=1, value=item["cantidad"], key=f"cant_{i}", label_visibility="collapsed")
                    if nueva_cant != item["cantidad"]:
                        st.session_state.carrito[i]["cantidad"] = nueva_cant
                        st.session_state.carrito[i]["subtotal"] = nueva_cant * item["precio_unitario"]
                        st.rerun()
                with col_x:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.carrito.pop(i)
                        st.rerun()
                total += item["subtotal"]
                st.markdown("---")
            
            st.markdown(f"### Total: **{formato_moneda(total)}**")
            
            metodo = st.selectbox("💳 Método de pago", ["efectivo", "tarjeta", "mixto"])
            monto_recibido = 0.0
            if metodo == "efectivo":
                monto_recibido = st.number_input("💵 Monto recibido", min_value=total, value=total, step=0.5)
                if monto_recibido >= total:
                    st.info(f"Cambio: **{formato_moneda(monto_recibido - total)}**")
            
            if st.button("✅ Cobrar", type="primary", use_container_width=True):
                u = usuario_actual()
                ok, msg, venta = registrar_venta(
                    items=st.session_state.carrito,
                    metodo_pago=metodo,
                    usuario_id=u["id"],
                    monto_recibido=monto_recibido
                )
                if ok:
                    st.success(f"✅ {msg}")
                    st.balloons()
                    st.session_state.carrito = []
                    st.rerun()
                else:
                    st.error(msg)


def pagina_inventario():
    from modules.inventario import (listar_productos, agregar_producto,
                                     actualizar_producto, eliminar_producto, obtener_categorias)
    from utils.db import formato_moneda
    
    st.markdown("""
    <div class="app-header">
        <span style="font-size:1.8rem">📦</span>
        <div>
            <h2 style="margin:0; color:white">Inventario</h2>
            <p style="margin:0; opacity:0.7; font-size:0.9rem">Gestión de productos</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_lista, tab_agregar = st.tabs(["📋 Lista de productos", "➕ Agregar producto"])
    
    with tab_lista:
        col_filtros = st.columns(3)
        with col_filtros[0]:
            seccion = st.selectbox("Sección", ["Todas", "abarrotes", "ferreteria"])
        with col_filtros[1]:
            busqueda = st.text_input("🔍 Buscar", placeholder="Nombre o código...")
        
        productos = listar_productos(seccion=None if seccion == "Todas" else seccion)
        if busqueda:
            productos = [p for p in productos if busqueda.lower() in p["nombre"].lower()]
        
        if productos:
            for p in productos:
                col1, col2, col3, col4 = st.columns([2.5, 1, 1, 1])
                stock_color = "🔴" if p["stock"] <= p.get("stock_minimo", 0) else "🟢"
                with col1:
                    st.write(f"**{p['nombre']}** `{p.get('codigo', 'S/C')}`")
                    st.write(f"{p.get('categoria', '')} · {p.get('seccion', '').capitalize()}")
                with col2:
                    st.write(f"Compra: {formato_moneda(p['precio_compra'])}")
                    st.write(f"Venta: **{formato_moneda(p['precio_venta'])}**")
                with col3:
                    st.write(f"{stock_color} Stock: **{p['stock']}**")
                    st.write(f"Mín: {p.get('stock_minimo', 0)}")
                with col4:
                    if tiene_permiso("editar_inventario"):
                        if st.button("✏️ Editar", key=f"edit_{p['id']}"):
                            st.session_state[f"editando_{p['id']}"] = True
                
                # Editor inline
                if st.session_state.get(f"editando_{p['id']}"):
                    with st.expander(f"Editando: {p['nombre']}", expanded=True):
                        with st.form(f"form_edit_{p['id']}"):
                            c1, c2, c3 = st.columns(3)
                            nuevo_precio_compra = c1.number_input("Precio compra", value=p["precio_compra"], min_value=0.0, step=0.5)
                            nuevo_precio_venta = c2.number_input("Precio venta", value=p["precio_venta"], min_value=0.0, step=0.5)
                            nuevo_stock = c3.number_input("Stock actual", value=p["stock"], min_value=0)
                            nuevo_stock_min = c1.number_input("Stock mínimo", value=p.get("stock_minimo", 0), min_value=0)
                            
                            col_guardar, col_cancel, col_eliminar = st.columns(3)
                            if col_guardar.form_submit_button("💾 Guardar", type="primary"):
                                ok, msg = actualizar_producto(p["id"], {
                                    "precio_compra": nuevo_precio_compra,
                                    "precio_venta": nuevo_precio_venta,
                                    "stock": nuevo_stock,
                                    "stock_minimo": nuevo_stock_min
                                })
                                if ok:
                                    st.success(msg)
                                    del st.session_state[f"editando_{p['id']}"]
                                    st.rerun()
                                else:
                                    st.error(msg)
                            if col_cancel.form_submit_button("❌ Cancelar"):
                                del st.session_state[f"editando_{p['id']}"]
                                st.rerun()
                            if col_eliminar.form_submit_button("🗑️ Desactivar"):
                                eliminar_producto(p["id"])
                                del st.session_state[f"editando_{p['id']}"]
                                st.rerun()
                
                st.markdown("---")
        else:
            st.info("No hay productos que mostrar.")
    
    with tab_agregar:
        if tiene_permiso("editar_inventario"):
            categorias = obtener_categorias()
            with st.form("form_agregar"):
                st.subheader("Nuevo producto")
                c1, c2 = st.columns(2)
                nombre = c1.text_input("Nombre del producto *")
                codigo = c2.text_input("Código de barras")
                
                c3, c4 = st.columns(2)
                seccion_nueva = c3.selectbox("Sección *", ["abarrotes", "ferreteria"])
                cats = categorias.get(seccion_nueva, [])
                categoria = c4.selectbox("Categoría *", cats)
                
                c5, c6, c7 = st.columns(3)
                precio_compra = c5.number_input("Precio compra *", min_value=0.0, step=0.5)
                precio_venta = c6.number_input("Precio venta *", min_value=0.0, step=0.5)
                stock_inicial = c7.number_input("Stock inicial *", min_value=0)
                stock_min = c5.number_input("Stock mínimo", min_value=0, value=5)
                unidad = c6.selectbox("Unidad", ["pieza", "kg", "litro", "caja", "paquete", "metro"])
                
                if st.form_submit_button("➕ Agregar producto", type="primary"):
                    if not nombre:
                        st.error("El nombre es obligatorio.")
                    elif precio_venta <= 0:
                        st.error("El precio de venta debe ser mayor a 0.")
                    else:
                        ok, msg = agregar_producto({
                            "nombre": nombre, "codigo": codigo,
                            "categoria": categoria, "seccion": seccion_nueva,
                            "precio_compra": precio_compra, "precio_venta": precio_venta,
                            "stock": stock_inicial, "stock_minimo": stock_min, "unidad": unidad
                        })
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.warning("No tienes permisos para agregar productos.")


def pagina_caja():
    from modules.caja import abrir_caja, hacer_corte, estado_caja, historial_cortes
    from modules.ventas import resumen_del_dia
    from utils.db import formato_moneda
    
    st.markdown("""
    <div class="app-header">
        <span style="font-size:1.8rem">💰</span>
        <div>
            <h2 style="margin:0; color:white">Caja y Cortes</h2>
            <p style="margin:0; opacity:0.7; font-size:0.9rem">Control de efectivo y cierre del día</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    caja = estado_caja()
    resumen = resumen_del_dia()
    
    if not caja.get("abierta"):
        st.info("📪 La caja está cerrada.")
        if tiene_permiso("hacer_corte"):
            with st.form("form_abrir_caja"):
                fondo = st.number_input("💵 Fondo inicial", min_value=0.0, value=500.0, step=50.0)
                if st.form_submit_button("🔓 Abrir caja", type="primary"):
                    u = usuario_actual()
                    ok, msg = abrir_caja(fondo, u["id"])
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
    else:
        st.success(f"✅ Caja abierta desde {caja.get('hora_apertura', '')} | Fondo: {formato_moneda(caja.get('fondo_inicial', 0))}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💵 Efectivo en ventas", formato_moneda(resumen["efectivo"]))
        col2.metric("💳 Tarjeta", formato_moneda(resumen["tarjeta"]))
        col3.metric("📈 Utilidad estimada", formato_moneda(resumen["utilidad"]))
        
        if tiene_permiso("hacer_corte"):
            st.subheader("🔒 Hacer corte de caja")
            with st.form("form_corte"):
                efectivo_contado = st.number_input("💵 Efectivo contado en caja", min_value=0.0, step=10.0)
                notas = st.text_area("Notas (opcional)")
                if st.form_submit_button("✅ Realizar corte", type="primary"):
                    u = usuario_actual()
                    ok, msg, corte = hacer_corte(u["id"], efectivo_contado, notas)
                    if ok:
                        st.success(msg)
                        dif = corte["diferencia"]
                        if abs(dif) < 1:
                            st.info("✅ La caja cuadra perfectamente.")
                        elif dif > 0:
                            st.warning(f"⚠️ Sobrante de caja: {formato_moneda(dif)}")
                        else:
                            st.error(f"❌ Faltante de caja: {formato_moneda(abs(dif))}")
                        st.rerun()
                    else:
                        st.error(msg)
    
    st.subheader("📋 Historial de cortes")
    cortes = historial_cortes()
    if cortes:
        for c in cortes[:10]:
            with st.expander(f"📅 {c['fecha']} — Total: {formato_moneda(c['ventas_totales'])} | Utilidad: {formato_moneda(c['utilidad_ventas'])}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Ventas", c["num_ventas"])
                col2.metric("Ingresos", formato_moneda(c["ventas_totales"]))
                col3.metric("Utilidad", formato_moneda(c["utilidad_ventas"]))
                diferencia = c.get("diferencia", 0)
                if abs(diferencia) < 1:
                    st.success("✅ Caja cuadrada")
                else:
                    estado = "sobrante" if diferencia > 0 else "faltante"
                    st.warning(f"⚠️ {estado.capitalize()}: {formato_moneda(abs(diferencia))}")
    else:
        st.info("No hay cortes registrados aún.")


def pagina_recargas():
    from modules.recargas import registrar_recarga, recargas_del_dia, obtener_operadoras
    from utils.db import formato_moneda
    
    st.markdown("""
    <div class="app-header">
        <span style="font-size:1.8rem">📱</span>
        <div>
            <h2 style="margin:0; color:white">Recargas Telefónicas</h2>
            <p style="margin:0; opacity:0.7; font-size:0.9rem">Registra recargas del día</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_form, col_lista = st.columns([1, 1.2])
    
    with col_form:
        st.subheader("Nueva recarga")
        operadoras = obtener_operadoras()
        with st.form("form_recarga"):
            telefono = st.text_input("📞 Número de teléfono", max_chars=10, placeholder="10 dígitos")
            operadora = st.selectbox("📡 Operadora", operadoras)
            monto = st.selectbox("💵 Monto", [20, 30, 50, 100, 150, 200, 300, 500])
            
            if st.form_submit_button("✅ Registrar recarga", type="primary"):
                if len(telefono) != 10 or not telefono.isdigit():
                    st.error("Ingresa un número de 10 dígitos.")
                else:
                    u = usuario_actual()
                    ok, msg = registrar_recarga(telefono, operadora, float(monto), u["id"])
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
    
    with col_lista:
        st.subheader("📋 Recargas de hoy")
        recargas = recargas_del_dia()
        if recargas:
            total = sum(r["monto"] for r in recargas)
            st.metric("Total recargas del día", formato_moneda(total))
            for r in reversed(recargas):
                st.write(f"📱 **{r['telefono']}** ({r['operadora']}) — {formato_moneda(r['monto'])} — {r['hora']}")
        else:
            st.info("No hay recargas registradas hoy.")


def pagina_usuarios():
    from modules.auth import crear_usuario, listar_usuarios, actualizar_usuario, obtener_roles
    
    st.markdown("""
    <div class="app-header">
        <span style="font-size:1.8rem">👥</span>
        <div>
            <h2 style="margin:0; color:white">Gestión de Usuarios</h2>
            <p style="margin:0; opacity:0.7; font-size:0.9rem">Administra accesos y roles</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_lista, tab_nuevo = st.tabs(["👥 Usuarios activos", "➕ Nuevo usuario"])
    roles = obtener_roles()
    
    with tab_lista:
        usuarios = listar_usuarios()
        for u in usuarios:
            col1, col2, col3 = st.columns([2, 1, 1])
            rol_info = roles.get(u["rol"], {})
            color = rol_info.get("color", "#aaa")
            with col1:
                st.markdown(f"**{u['nombre']}** `@{u['usuario']}`")
                st.markdown(f"<span style='color:{color}; font-size:0.85rem'>● {rol_info.get('nombre', u['rol'])}</span>", unsafe_allow_html=True)
            with col2:
                estado = "✅ Activo" if u.get("activo") else "❌ Inactivo"
                st.write(estado)
                st.write(f"Alta: {u.get('fecha_creacion', '—')}")
            with col3:
                u_actual = usuario_actual()
                if u["id"] != u_actual["id"]:  # No puede editarse a sí mismo aquí
                    nuevo_estado = not u.get("activo", True)
                    label = "🚫 Desactivar" if u.get("activo") else "✅ Activar"
                    if st.button(label, key=f"toggle_{u['id']}"):
                        actualizar_usuario(u["id"], {"activo": nuevo_estado})
                        st.rerun()
            st.markdown("---")
    
    with tab_nuevo:
        with st.form("form_nuevo_usuario"):
            st.subheader("Crear nuevo usuario")
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre completo *")
            usuario_nuevo = c2.text_input("Usuario (login) *")
            password = c1.text_input("Contraseña *", type="password")
            rol = c2.selectbox("Rol *", list(roles.keys()), format_func=lambda r: roles[r]["nombre"])
            
            # Mostrar descripción del rol
            if rol:
                st.info(f"ℹ️ {roles[rol]['descripcion']}")
            
            if st.form_submit_button("➕ Crear usuario", type="primary"):
                if not nombre or not usuario_nuevo or not password:
                    st.error("Todos los campos son obligatorios.")
                elif len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    ok, msg = crear_usuario(nombre, usuario_nuevo, password, rol)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)


def pagina_configuracion():
    from utils.db import leer_json, escribir_json
    
    st.markdown("""
    <div class="app-header">
        <span style="font-size:1.8rem">⚙️</span>
        <div>
            <h2 style="margin:0; color:white">Configuración</h2>
            <p style="margin:0; opacity:0.7; font-size:0.9rem">Ajustes de la tienda</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    config = leer_json("config_tienda.json")
    tienda = config.get("tienda", {})
    
    with st.form("form_config"):
        st.subheader("🏪 Datos de la tienda")
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre de la tienda", value=tienda.get("nombre", ""))
        slogan = c2.text_input("Slogan", value=tienda.get("slogan", ""))
        direccion = c1.text_input("Dirección", value=tienda.get("direccion", ""))
        telefono = c2.text_input("Teléfono", value=tienda.get("telefono", ""))
        ticket_pie = st.text_area("Mensaje en ticket", value=tienda.get("ticket_pie", ""))
        
        if st.form_submit_button("💾 Guardar configuración", type="primary"):
            config["tienda"].update({
                "nombre": nombre, "slogan": slogan,
                "direccion": direccion, "telefono": telefono,
                "ticket_pie": ticket_pie
            })
            if escribir_json("config_tienda.json", config):
                st.success("✅ Configuración guardada.")
            else:
                st.error("Error al guardar.")


# ── Router principal ─────────────────────────────────────────────────────────
def main():
    if not esta_autenticado():
        pantalla_login()
        return
    
    sidebar_navegacion()
    
    # Página por defecto según rol
    if "pagina_actual" not in st.session_state:
        u = usuario_actual()
        if tiene_permiso("ver_dashboard"):
            st.session_state["pagina_actual"] = "dashboard"
        elif tiene_permiso("hacer_ventas"):
            st.session_state["pagina_actual"] = "pos"
        elif tiene_permiso("ver_inventario"):
            st.session_state["pagina_actual"] = "inventario"
        else:
            st.session_state["pagina_actual"] = "recargas"
    
    pagina = st.session_state.get("pagina_actual", "dashboard")
    
    rutas = {
        "dashboard": (pagina_dashboard, "ver_dashboard"),
        "pos": (pagina_pos, "hacer_ventas"),
        "inventario": (pagina_inventario, "ver_inventario"),
        "caja": (pagina_caja, "ver_caja"),
        "recargas": (pagina_recargas, "hacer_recargas"),
        "usuarios": (pagina_usuarios, "gestionar_usuarios"),
        "configuracion": (pagina_configuracion, "configuracion"),
    }
    
    if pagina in rutas:
        func, permiso = rutas[pagina]
        if tiene_permiso(permiso):
            func()
        else:
            st.error("🚫 No tienes permisos para acceder a esta sección.")
    else:
        pagina_dashboard()


if __name__ == "__main__":
    main()
