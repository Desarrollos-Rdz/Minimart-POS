import streamlit as st
from modules.inventario import buscar_producto, listar_productos
from modules.ventas import registrar_venta
from modules.auth import usuario_actual
from utils.db import formato_moneda

st.markdown("""
<div class="page-header">
    <span style="font-size:2rem;">🛒</span>
    <div>
        <h2 style="margin:0; color:white; font-weight:700;">Punto de Venta</h2>
        <p style="margin:0; opacity:0.75; font-size:0.88rem;">Registra ventas rápidamente</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Inicializar carrito
if "carrito" not in st.session_state:
    st.session_state.carrito = []

col_busq, col_carrito = st.columns([1.3, 1], gap="large")

# ── Panel de búsqueda ─────────────────────────────────────────────────────────
with col_busq:
    st.subheader("🔍 Agregar productos")

    tab_buscar, tab_todos = st.tabs(["Buscar", "Ver todos"])

    with tab_buscar:
        busqueda = st.text_input("Nombre, código o categoría", placeholder="Ej: Coca Cola, FER001...",
                                  label_visibility="collapsed")
        if busqueda:
            resultados = buscar_producto(busqueda)
            if resultados:
                for p in resultados[:10]:
                    c1, c2, c3 = st.columns([3, 1.2, 0.8])
                    with c1:
                        st.write(f"**{p['nombre']}**")
                        st.caption(f"{p.get('categoria','')} · {p.get('seccion','').capitalize()}")
                    with c2:
                        st.write(f"**{formato_moneda(p['precio_venta'])}**")
                        stock_color = "🔴" if p["stock"] == 0 else ("🟡" if p["stock"] <= p.get("stock_minimo",0) else "🟢")
                        st.caption(f"{stock_color} Stock: {p['stock']}")
                    with c3:
                        disabled = p["stock"] == 0
                        if st.button("➕", key=f"add_{p['id']}", disabled=disabled, help="Agregar al carrito"):
                            _agregar_al_carrito(p)
                    st.divider()
            else:
                st.info("Sin resultados.")
        else:
            st.caption("Escribe para buscar productos...")

    with tab_todos:
        seccion_filtro = st.radio("Sección", ["Todas", "Abarrotes", "Ferretería"], horizontal=True)
        sec = None if seccion_filtro == "Todas" else seccion_filtro.lower().replace("í","i")
        productos_lista = listar_productos(seccion=sec)
        for p in productos_lista:
            c1, c2, c3 = st.columns([3, 1.2, 0.8])
            with c1:
                st.write(f"**{p['nombre']}**")
                st.caption(p.get("categoria", ""))
            with c2:
                st.write(f"**{formato_moneda(p['precio_venta'])}**")
                stock_color = "🔴" if p["stock"] == 0 else ("🟡" if p["stock"] <= p.get("stock_minimo",0) else "🟢")
                st.caption(f"{stock_color} {p['stock']}")
            with c3:
                disabled = p["stock"] == 0
                if st.button("➕", key=f"all_{p['id']}", disabled=disabled):
                    _agregar_al_carrito(p)
            st.divider()


def _agregar_al_carrito(p):
    for item in st.session_state.carrito:
        if item["producto_id"] == p["id"]:
            if item["cantidad"] < p["stock"]:
                item["cantidad"] += 1
                item["subtotal"] = round(item["cantidad"] * item["precio_unitario"], 2)
            else:
                st.warning(f"Stock máximo alcanzado ({p['stock']})")
            return
    if p["stock"] > 0:
        st.session_state.carrito.append({
            "producto_id": p["id"],
            "nombre": p["nombre"],
            "cantidad": 1,
            "precio_unitario": p["precio_venta"],
            "subtotal": p["precio_venta"]
        })
    st.rerun()


# ── Panel de carrito ──────────────────────────────────────────────────────────
with col_carrito:
    n = len(st.session_state.carrito)
    st.subheader(f"🧾 Carrito ({n} {'producto' if n == 1 else 'productos'})")

    if not st.session_state.carrito:
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem; color:#bbb;">
            <div style="font-size:3rem;">🛒</div>
            <p>El carrito está vacío.<br>Busca y agrega productos.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        total = 0
        to_remove = None

        for i, item in enumerate(st.session_state.carrito):
            ca, cb, cc = st.columns([2.5, 1.2, 0.5])
            with ca:
                st.write(f"**{item['nombre']}**")
                st.caption(f"{formato_moneda(item['precio_unitario'])} c/u")
            with cb:
                nueva = st.number_input("", min_value=1, value=item["cantidad"],
                                         key=f"qty_{i}", label_visibility="collapsed")
                if nueva != item["cantidad"]:
                    st.session_state.carrito[i]["cantidad"] = nueva
                    st.session_state.carrito[i]["subtotal"] = round(nueva * item["precio_unitario"], 2)
                    st.rerun()
                st.caption(f"= **{formato_moneda(item['subtotal'])}**")
            with cc:
                if st.button("🗑️", key=f"rm_{i}", help="Quitar"):
                    to_remove = i

            total += item["subtotal"]

        if to_remove is not None:
            st.session_state.carrito.pop(to_remove)
            st.rerun()

        st.markdown("---")

        # Descuento
        descuento = st.number_input("🏷️ Descuento ($)", min_value=0.0, max_value=float(total),
                                     value=0.0, step=5.0)
        total_final = total - descuento

        st.markdown(f"""
        <div style="background:#f8f9fa; border-radius:10px; padding:1rem; margin:0.5rem 0;">
            <div style="display:flex; justify-content:space-between; color:#666;">
                <span>Subtotal</span><span>{formato_moneda(total)}</span>
            </div>
            {"" if descuento == 0 else f'<div style="display:flex; justify-content:space-between; color:#e94560;"><span>Descuento</span><span>-{formato_moneda(descuento)}</span></div>'}
            <div style="display:flex; justify-content:space-between; font-weight:700; font-size:1.2rem; margin-top:0.5rem; color:#1a1a2e;">
                <span>TOTAL</span><span>{formato_moneda(total_final)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        metodo = st.selectbox("💳 Método de pago", ["efectivo", "tarjeta", "mixto"],
                               format_func=lambda x: {"efectivo":"💵 Efectivo",
                                                       "tarjeta":"💳 Tarjeta",
                                                       "mixto":"🔀 Mixto"}[x])
        monto_recibido = total_final
        if metodo == "efectivo":
            monto_recibido = st.number_input("💵 Monto recibido ($)", min_value=total_final,
                                              value=total_final, step=10.0)
            cambio = monto_recibido - total_final
            if cambio > 0:
                st.success(f"💰 Cambio: **{formato_moneda(cambio)}**")

        ca, cb = st.columns(2)
        with ca:
            if st.button("🗑️ Vaciar", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()
        with cb:
            if st.button("✅ Cobrar", type="primary", use_container_width=True):
                u = usuario_actual()
                ok, msg, venta = registrar_venta(
                    items=st.session_state.carrito,
                    metodo_pago=metodo,
                    usuario_id=u["id"],
                    monto_recibido=monto_recibido,
                    descuento=descuento
                )
                if ok:
                    st.success(f"✅ Venta registrada — Total: {formato_moneda(total_final)}")
                    st.balloons()
                    st.session_state.carrito = []
                    st.rerun()
                else:
                    st.error(msg)