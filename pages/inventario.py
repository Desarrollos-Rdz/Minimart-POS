import streamlit as st
from modules.inventario import (listar_productos, agregar_producto, actualizar_producto,
                                 eliminar_producto, productos_bajo_stock, obtener_categorias)
from modules.auth import tiene_permiso
from utils.db import formato_moneda

st.markdown("""
<div class="page-header">
    <span style="font-size:2rem;">📦</span>
    <div>
        <h2 style="margin:0; color:white; font-weight:700;">Inventario</h2>
        <p style="margin:0; opacity:0.75; font-size:0.88rem;">Gestión de productos y stock</p>
    </div>
</div>
""", unsafe_allow_html=True)

tab_lista, tab_agregar, tab_alertas = st.tabs(["📋 Productos", "➕ Agregar", "⚠️ Alertas de stock"])

# ── Lista de productos ────────────────────────────────────────────────────────
with tab_lista:
    c1, c2, c3 = st.columns([1.5, 1, 2])
    with c1:
        seccion = st.selectbox("Sección", ["Todas", "abarrotes", "ferreteria"],
                                format_func=lambda x: {"Todas":"Todas","abarrotes":"🛒 Abarrotes","ferreteria":"🔧 Ferretería"}[x])
    with c3:
        busqueda = st.text_input("🔍 Buscar producto", placeholder="Nombre o código...")

    productos = listar_productos(seccion=None if seccion == "Todas" else seccion)
    if busqueda:
        productos = [p for p in productos if busqueda.lower() in p["nombre"].lower()
                     or busqueda.lower() in p.get("codigo","").lower()]

    st.caption(f"{len(productos)} productos encontrados")
    st.markdown("---")

    for p in productos:
        stock_ok = p["stock"] > p.get("stock_minimo", 0)
        stock_icon = "🟢" if stock_ok else ("🔴" if p["stock"] == 0 else "🟡")

        with st.container():
            ca, cb, cc, cd = st.columns([2.5, 1.5, 1.5, 1])
            with ca:
                seccion_label = {"abarrotes":"🛒","ferreteria":"🔧"}.get(p.get("seccion",""), "📦")
                st.write(f"{seccion_label} **{p['nombre']}**")
                st.caption(f"`{p.get('codigo','S/C')}` · {p.get('categoria','')} · {p.get('unidad','pieza')}")
            with cb:
                st.write(f"Compra: {formato_moneda(p['precio_compra'])}")
                st.write(f"Venta: **{formato_moneda(p['precio_venta'])}**")
                margen = ((p['precio_venta'] - p['precio_compra']) / p['precio_venta'] * 100) if p['precio_venta'] > 0 else 0
                st.caption(f"Margen: {margen:.1f}%")
            with cc:
                st.write(f"{stock_icon} Stock: **{p['stock']}**")
                st.caption(f"Mín: {p.get('stock_minimo', 0)}")
            with cd:
                if tiene_permiso("editar_inventario"):
                    if st.button("✏️", key=f"edit_{p['id']}", help="Editar"):
                        st.session_state[f"ed_{p['id']}"] = not st.session_state.get(f"ed_{p['id']}", False)
                        st.rerun()

        # Editor inline
        if st.session_state.get(f"ed_{p['id']}", False):
            with st.expander(f"✏️ Editando: {p['nombre']}", expanded=True):
                with st.form(f"f_edit_{p['id']}"):
                    e1, e2, e3, e4 = st.columns(4)
                    npc = e1.number_input("Precio compra", value=float(p["precio_compra"]), min_value=0.0, step=0.5)
                    npv = e2.number_input("Precio venta", value=float(p["precio_venta"]), min_value=0.0, step=0.5)
                    ns  = e3.number_input("Stock actual", value=int(p["stock"]), min_value=0)
                    nm  = e4.number_input("Stock mínimo", value=int(p.get("stock_minimo",0)), min_value=0)

                    g, x, d = st.columns(3)
                    if g.form_submit_button("💾 Guardar", type="primary"):
                        ok, msg = actualizar_producto(p["id"], {
                            "precio_compra": npc, "precio_venta": npv,
                            "stock": ns, "stock_minimo": nm
                        })
                        st.success(msg) if ok else st.error(msg)
                        if ok:
                            st.session_state[f"ed_{p['id']}"] = False
                            st.rerun()
                    if x.form_submit_button("❌ Cancelar"):
                        st.session_state[f"ed_{p['id']}"] = False
                        st.rerun()
                    if d.form_submit_button("🗑️ Desactivar"):
                        eliminar_producto(p["id"])
                        st.session_state[f"ed_{p['id']}"] = False
                        st.rerun()

        st.markdown("---")

# ── Agregar producto ──────────────────────────────────────────────────────────
with tab_agregar:
    if not tiene_permiso("editar_inventario"):
        st.warning("🚫 No tienes permisos para agregar productos.")
    else:
        categorias = obtener_categorias()
        with st.form("form_nuevo_producto", border=False):
            st.markdown('<div class="pos-card">', unsafe_allow_html=True)
            st.subheader("Datos del producto")

            c1, c2 = st.columns(2)
            nombre   = c1.text_input("Nombre del producto *")
            codigo   = c2.text_input("Código de barras")

            c3, c4 = st.columns(2)
            seccion_n = c3.selectbox("Sección *", ["abarrotes", "ferreteria"],
                                      format_func=lambda x: {"abarrotes":"🛒 Abarrotes","ferreteria":"🔧 Ferretería"}[x])
            cats = categorias.get(seccion_n, [])
            categoria = c4.selectbox("Categoría *", cats)

            st.subheader("Precios y stock")
            c5, c6, c7, c8 = st.columns(4)
            precio_compra  = c5.number_input("Precio compra *",  min_value=0.0, step=0.5, format="%.2f")
            precio_venta   = c6.number_input("Precio venta *",   min_value=0.0, step=0.5, format="%.2f")
            stock_inicial  = c7.number_input("Stock inicial *",  min_value=0)
            stock_min      = c8.number_input("Stock mínimo",     min_value=0, value=5)
            unidad = st.selectbox("Unidad de medida", ["pieza","kg","litro","caja","paquete","metro","par"])

            if precio_compra > 0 and precio_venta > 0:
                margen = (precio_venta - precio_compra) / precio_venta * 100
                st.info(f"📊 Margen de ganancia: **{margen:.1f}%** ({formato_moneda(precio_venta - precio_compra)} por unidad)")

            st.markdown('</div>', unsafe_allow_html=True)

            if st.form_submit_button("➕ Agregar producto", type="primary", use_container_width=True):
                if not nombre:
                    st.error("El nombre es obligatorio.")
                elif precio_venta <= 0:
                    st.error("El precio de venta debe ser mayor a 0.")
                else:
                    ok, msg = agregar_producto({
                        "nombre": nombre, "codigo": codigo,
                        "categoria": categoria, "seccion": seccion_n,
                        "precio_compra": precio_compra, "precio_venta": precio_venta,
                        "stock": stock_inicial, "stock_minimo": stock_min, "unidad": unidad
                    })
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        st.rerun()

# ── Alertas de stock ──────────────────────────────────────────────────────────
with tab_alertas:
    bajos = productos_bajo_stock()
    if not bajos:
        st.success("✅ Todos los productos tienen stock por encima del mínimo.")
    else:
        st.warning(f"⚠️ {len(bajos)} productos necesitan reabastecerse")
        for p in bajos:
            urgente = p["stock"] == 0
            color = "#ffebee" if urgente else "#fff8e1"
            borde = "#e94560" if urgente else "#ffc107"
            st.markdown(f"""
            <div style="background:{color}; border-left:4px solid {borde};
                        padding:0.75rem 1rem; border-radius:0 8px 8px 0; margin:0.4rem 0;">
                <strong>{"🔴 AGOTADO" if urgente else "🟡"} {p['nombre']}</strong>
                <span style="float:right; color:#888; font-size:0.85rem;">{p.get('seccion','').capitalize()}</span><br>
                Stock actual: <strong style="color:{'#e94560' if urgente else '#e65100'};">{p['stock']}</strong>
                · Mínimo: {p.get('stock_minimo',0)}
                · Venta: {formato_moneda(p['precio_venta'])}
            </div>
            """, unsafe_allow_html=True)