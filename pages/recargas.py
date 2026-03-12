import streamlit as st
from modules.recargas import registrar_recarga, recargas_del_dia, historial_recargas, obtener_operadoras
from modules.auth import usuario_actual
from utils.db import formato_moneda, fecha_hoy

st.markdown("""
<div class="page-header">
    <span style="font-size:2rem;">📱</span>
    <div>
        <h2 style="margin:0; color:white; font-weight:700;">Recargas Telefónicas</h2>
        <p style="margin:0; opacity:0.75; font-size:0.88rem;">Registra y consulta recargas</p>
    </div>
</div>
""", unsafe_allow_html=True)

tab_nueva, tab_hoy, tab_historial = st.tabs(["➕ Nueva recarga", "📋 Recargas de hoy", "📅 Historial"])

operadoras = obtener_operadoras()
MONTOS = [10, 20, 30, 50, 100, 150, 200, 300, 500]

with tab_nueva:
    col_form, col_resumen = st.columns([1, 1.2], gap="large")

    with col_form:
        with st.form("form_recarga", border=False):
            st.markdown('<div class="pos-card">', unsafe_allow_html=True)
            st.subheader("Datos de la recarga")

            telefono = st.text_input("📞 Número de teléfono", max_chars=10,
                                      placeholder="10 dígitos", help="Solo números, sin espacios ni guiones")
            operadora = st.selectbox("📡 Operadora", operadoras)
            monto = st.select_slider("💵 Monto ($)", options=MONTOS, value=50)

            st.markdown(f"""
            <div style="background:#f0f9ff; border-radius:8px; padding:1rem; margin:0.5rem 0; text-align:center;">
                <div style="font-size:0.85rem; color:#666;">Total a cobrar</div>
                <div style="font-size:2rem; font-weight:800; color:#0f3460;">{formato_moneda(monto)}</div>
                <div style="font-size:0.85rem; color:#888;">{operadora} · {telefono if telefono else '##########'}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.form_submit_button("✅ Registrar recarga", type="primary", use_container_width=True):
                if len(telefono) != 10 or not telefono.isdigit():
                    st.error("❌ Ingresa un número de teléfono válido de 10 dígitos.")
                else:
                    u = usuario_actual()
                    ok, msg = registrar_recarga(telefono, operadora, float(monto), u["id"])
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(msg)

    with col_resumen:
        st.subheader("📊 Resumen del día")
        recargas_hoy = recargas_del_dia()
        total_hoy = sum(r["monto"] for r in recargas_hoy)

        c1, c2 = st.columns(2)
        c1.metric("Total recargado", formato_moneda(total_hoy))
        c2.metric("Número de recargas", len(recargas_hoy))

        if recargas_hoy:
            # Resumen por operadora
            por_operadora = {}
            for r in recargas_hoy:
                op = r["operadora"]
                por_operadora[op] = por_operadora.get(op, 0) + r["monto"]
            
            st.markdown("**Por operadora:**")
            for op, total_op in sorted(por_operadora.items(), key=lambda x: -x[1]):
                pct = int(total_op / total_hoy * 100) if total_hoy > 0 else 0
                col_op, col_val = st.columns([2, 1])
                col_op.write(f"📡 {op}")
                col_val.write(f"**{formato_moneda(total_op)}**")
                st.progress(pct)

with tab_hoy:
    recargas_hoy = recargas_del_dia()
    if not recargas_hoy:
        st.info("No hay recargas registradas hoy.")
    else:
        total = sum(r["monto"] for r in recargas_hoy)
        st.metric("Total del día", formato_moneda(total))
        st.markdown("---")
        for r in reversed(recargas_hoy):
            ca, cb, cc, cd = st.columns([1.5, 1.2, 1, 0.8])
            ca.write(f"📱 **{r['telefono']}**")
            cb.write(r["operadora"])
            cc.write(f"**{formato_moneda(r['monto'])}**")
            cd.write(r["hora"])

with tab_historial:
    st.subheader("Filtrar por rango de fechas")
    c1, c2 = st.columns(2)
    from datetime import date, timedelta
    fi = c1.date_input("Desde", value=date.today() - timedelta(days=7))
    ff = c2.date_input("Hasta", value=date.today())

    recargas = historial_recargas(str(fi), str(ff))
    if not recargas:
        st.info("No hay recargas en ese período.")
    else:
        total_periodo = sum(r["monto"] for r in recargas)
        st.metric(f"Total del período ({len(recargas)} recargas)", formato_moneda(total_periodo))
        st.markdown("---")
        for r in recargas:
            ca, cb, cc, cd, ce = st.columns([1.2, 1.5, 1.2, 1, 0.8])
            ca.write(r["fecha"])
            cb.write(f"📱 **{r['telefono']}**")
            cc.write(r["operadora"])
            cd.write(f"**{formato_moneda(r['monto'])}**")
            ce.write(r["hora"])