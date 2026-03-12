import streamlit as st
from modules.ventas import resumen_del_dia, historial_ventas
from modules.inventario import productos_bajo_stock
from modules.recargas import recargas_del_dia
from utils.db import formato_moneda, fecha_hoy

st.markdown("""
<div class="page-header">
    <span style="font-size:2rem;">🏠</span>
    <div>
        <h2 style="margin:0; color:white; font-weight:700;">Dashboard</h2>
        <p style="margin:0; opacity:0.75; font-size:0.88rem;">Resumen del día de hoy</p>
    </div>
</div>
""", unsafe_allow_html=True)

resumen = resumen_del_dia()
recargas_hoy = recargas_del_dia()
total_recargas = sum(r["monto"] for r in recargas_hoy)
bajos = productos_bajo_stock()

# ── Métricas principales ──────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Ingresos del día", formato_moneda(resumen["ingresos_totales"]))
c2.metric("📈 Utilidad estimada", formato_moneda(resumen["utilidad"]))
c3.metric("🛒 Ventas", resumen["total_ventas"])
c4.metric("📱 Recargas", formato_moneda(total_recargas), f"{len(recargas_hoy)} ops")
c5.metric("⚠️ Stock bajo", len(bajos), delta=f"-{len(bajos)}" if bajos else None,
          delta_color="inverse")

st.markdown("---")

col_izq, col_der = st.columns([1.1, 1])

with col_izq:
    st.subheader("💳 Desglose por método de pago")
    metodos = [
        ("💵 Efectivo", resumen["efectivo"]),
        ("💳 Tarjeta", resumen["tarjeta"]),
        ("🔀 Mixto", resumen["mixto"]),
    ]
    for label, valor in metodos:
        pct = (valor / resumen["ingresos_totales"] * 100) if resumen["ingresos_totales"] > 0 else 0
        col_label, col_val, col_bar = st.columns([1.5, 1, 2])
        col_label.write(label)
        col_val.write(f"**{formato_moneda(valor)}**")
        col_bar.progress(int(pct))

    st.markdown("---")
    st.subheader("📱 Últimas recargas del día")
    if recargas_hoy:
        for r in list(reversed(recargas_hoy))[:5]:
            st.write(f"📲 `{r['telefono']}` · {r['operadora']} · **{formato_moneda(r['monto'])}** · {r['hora']}")
    else:
        st.info("No hay recargas registradas hoy.")

with col_der:
    st.subheader("⚠️ Productos con stock bajo")
    if bajos:
        for p in bajos[:8]:
            st.markdown(f"""
            <div class="stock-alert">
                <strong>{p['nombre']}</strong>
                <span style="float:right; color:#999; font-size:0.85rem;">{p.get('seccion','').capitalize()}</span><br>
                <span style="color:#e65100;">Stock: <strong>{p['stock']}</strong></span>
                <span style="color:#aaa;"> / mínimo: {p.get('stock_minimo', 0)}</span>
            </div>
            """, unsafe_allow_html=True)
        if len(bajos) > 8:
            st.caption(f"...y {len(bajos)-8} más. Ve al módulo de inventario.")
    else:
        st.success("✅ Todos los productos tienen stock suficiente.")

    st.markdown("---")
    st.subheader("🕐 Últimas ventas")
    ventas_recientes = historial_ventas()[:5]
    if ventas_recientes:
        for v in ventas_recientes:
            icono = {"efectivo": "💵", "tarjeta": "💳", "mixto": "🔀"}.get(v["metodo_pago"], "💰")
            st.write(f"{icono} **{formato_moneda(v['total'])}** · {len(v['items'])} productos · {v['hora']}")
    else:
        st.info("No hay ventas registradas hoy.")