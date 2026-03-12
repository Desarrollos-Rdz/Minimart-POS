import streamlit as st
from modules.caja import abrir_caja, hacer_corte, estado_caja, historial_cortes
from modules.ventas import resumen_del_dia
from modules.recargas import recargas_del_dia
from modules.auth import usuario_actual, tiene_permiso
from utils.db import formato_moneda

st.markdown("""
<div class="page-header">
    <span style="font-size:2rem;">💰</span>
    <div>
        <h2 style="margin:0; color:white; font-weight:700;">Caja y Cortes</h2>
        <p style="margin:0; opacity:0.75; font-size:0.88rem;">Control de efectivo y cierre del día</p>
    </div>
</div>
""", unsafe_allow_html=True)

caja = estado_caja()
resumen = resumen_del_dia()
recargas_hoy = recargas_del_dia()
total_recargas = sum(r["monto"] for r in recargas_hoy)

tab_caja, tab_historial = st.tabs(["💰 Caja del día", "📋 Historial de cortes"])

with tab_caja:
    # ── Estado de la caja ─────────────────────────────────────────────────────
    if not caja.get("abierta"):
        st.info("📪 La caja está cerrada.")
        if tiene_permiso("hacer_corte"):
            st.subheader("🔓 Abrir caja")
            with st.form("form_abrir", border=False):
                st.markdown('<div class="pos-card">', unsafe_allow_html=True)
                fondo = st.number_input("💵 Fondo inicial de caja ($)", min_value=0.0,
                                         value=500.0, step=50.0)
                st.caption("Este es el efectivo con el que arranca la caja (cambio, monedas, etc.)")
                st.markdown('</div>', unsafe_allow_html=True)
                if st.form_submit_button("🔓 Abrir caja", type="primary"):
                    u = usuario_actual()
                    ok, msg = abrir_caja(fondo, u["id"])
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        st.rerun()
    else:
        st.success(f"✅ Caja abierta · Apertura: **{caja.get('hora_apertura','')}** · Fondo: **{formato_moneda(caja.get('fondo_inicial',0))}**")

        # Resumen en tiempo real
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💵 Efectivo en ventas", formato_moneda(resumen["efectivo"]))
        c2.metric("💳 Tarjeta", formato_moneda(resumen["tarjeta"]))
        c3.metric("📱 Recargas", formato_moneda(total_recargas))
        c4.metric("📈 Utilidad estimada", formato_moneda(resumen["utilidad"]))

        efectivo_esperado = caja.get("fondo_inicial", 0) + resumen["efectivo"] + total_recargas
        st.info(f"💰 Efectivo esperado en caja: **{formato_moneda(efectivo_esperado)}** "
                f"(fondo + ventas efectivo + recargas)")

        st.markdown("---")

        if tiene_permiso("hacer_corte"):
            st.subheader("🔒 Realizar corte de caja")
            with st.form("form_corte", border=False):
                st.markdown('<div class="pos-card">', unsafe_allow_html=True)
                efectivo_contado = st.number_input(
                    "💵 Efectivo físico contado en caja ($)",
                    min_value=0.0, value=float(efectivo_esperado), step=10.0
                )
                notas = st.text_area("📝 Notas del corte (opcional)", placeholder="Ej: se sacaron $200 para compra de cambio...")
                st.markdown('</div>', unsafe_allow_html=True)

                diferencia = efectivo_contado - efectivo_esperado
                if abs(diferencia) < 0.01:
                    st.success("✅ La caja cuadra perfectamente")
                elif diferencia > 0:
                    st.warning(f"⚠️ Sobrante estimado: **{formato_moneda(diferencia)}**")
                else:
                    st.error(f"❌ Faltante estimado: **{formato_moneda(abs(diferencia))}**")

                if st.form_submit_button("✅ Realizar corte y cerrar caja", type="primary", use_container_width=True):
                    u = usuario_actual()
                    ok, msg, corte = hacer_corte(u["id"], efectivo_contado, notas)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(msg)

with tab_historial:
    cortes = historial_cortes()
    if not cortes:
        st.info("No hay cortes registrados aún.")
    else:
        st.caption(f"{len(cortes)} cortes registrados")
        for c in cortes:
            dif = c.get("diferencia", 0)
            estado_icon = "✅" if abs(dif) < 1 else ("📈" if dif > 0 else "📉")
            with st.expander(f"{estado_icon} {c['fecha']} — Ventas: {formato_moneda(c['ventas_totales'])} · Utilidad: {formato_moneda(c['utilidad_ventas'])}"):
                ca, cb, cc, cd = st.columns(4)
                ca.metric("Num. ventas", c["num_ventas"])
                cb.metric("Efectivo", formato_moneda(c["ventas_efectivo"]))
                cc.metric("Tarjeta", formato_moneda(c["ventas_tarjeta"]))
                cd.metric("Recargas", formato_moneda(c.get("total_recargas", 0)))

                st.markdown("---")
                ce, cf, cg = st.columns(3)
                ce.metric("Fondo inicial", formato_moneda(c["fondo_inicial"]))
                cf.metric("Efectivo esperado", formato_moneda(c["efectivo_esperado"]))
                cg.metric("Efectivo contado", formato_moneda(c["efectivo_contado"]))

                if abs(dif) < 1:
                    st.success("✅ Caja cuadrada")
                elif dif > 0:
                    st.warning(f"📈 Sobrante: {formato_moneda(dif)}")
                else:
                    st.error(f"📉 Faltante: {formato_moneda(abs(dif))}")

                if c.get("notas"):
                    st.caption(f"📝 Notas: {c['notas']}")