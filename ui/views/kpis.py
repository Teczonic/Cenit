"""KPIs — motor de métricas con semáforo, meta y tendencia histórica."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from ui.api_client import ApiError
from ui.components import get_client

SEMAFORO = {"verde": "🟢", "ambar": "🟡", "rojo": "🔴", "sin_datos": "⚪"}
TEND = {"sube": "↑", "baja": "↓", "estable": "→"}


def _meta_label(k: dict) -> str:
    u = f' {k["unidad"]}' if k.get("unidad") else ""
    if k["direccion"] == "band":
        return f'objetivo {k.get("banda_min")}–{k.get("banda_max")}{u}'
    signo = "≤" if k["direccion"] == "down" else "≥"
    return f'meta {signo} {k.get("meta")}{u}'


def render():
    st.subheader("KPIs — tablero de control")
    st.caption("Cada indicador con meta, semáforo y tendencia. Una métrica es un dato, no un módulo.")

    client = get_client()
    try:
        data = client.kpi_overview()
    except ApiError as e:
        st.error(str(e))
        return

    r = data["resumen"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🟢 En meta", r.get("verde", 0))
    c2.metric("🟡 En alerta", r.get("ambar", 0), delta_color="off")
    c3.metric("🔴 Fuera de meta", r.get("rojo", 0), delta_color="inverse")
    c4.metric("⚪ Sin datos", r.get("sin_datos", 0), delta_color="off")

    st.divider()

    if not data["kpis"]:
        st.info("Aún no hay KPIs definidos. Créalos abajo.")
    else:
        cols = st.columns(2)
        for i, k in enumerate(data["kpis"]):
            with cols[i % 2]:
                with st.container(border=True):
                    u = f' {k["unidad"]}' if k.get("unidad") else ""
                    valor = f'{k["valor_actual"]:g}{u}' if k["valor_actual"] is not None else "—"
                    tend = f' {TEND.get(k["tendencia"], "")}' if k.get("tendencia") else ""
                    st.markdown(f'{SEMAFORO.get(k["estado"], "⚪")} **{k["nombre"]}**')
                    st.markdown(f'### {valor}{tend}')
                    st.caption(f'{_meta_label(k)} · fuente: {k["fuente"]}')
                    if len(k["historial"]) >= 2:
                        df = pd.DataFrame(k["historial"]).set_index("periodo_fin")[["valor"]]
                        st.line_chart(df, height=120)

    st.divider()

    with st.expander("➕ Crear KPI"):
        with st.form("nuevo_kpi", clear_on_submit=True):
            nombre = st.text_input("Nombre", placeholder="Change failure rate")
            clave = st.text_input("Clave única", placeholder="change_failure_rate")
            c1, c2 = st.columns(2)
            direccion = c1.selectbox("Dirección", ["up", "down", "band"],
                                     help="up: más es mejor · down: menos es mejor · band: rango objetivo")
            unidad = c2.text_input("Unidad", placeholder="%, días, tareas")
            if direccion == "band":
                b1, b2 = st.columns(2)
                banda_min = b1.number_input("Banda mínima", value=0.0)
                banda_max = b2.number_input("Banda máxima", value=10.0)
                meta = umbral = None
            else:
                m1, m2 = st.columns(2)
                meta = m1.number_input("Meta", value=0.0)
                umbral = m2.number_input("Umbral de alerta", value=0.0)
                banda_min = banda_max = None
            if st.form_submit_button("Crear KPI", type="primary"):
                if not nombre.strip() or not clave.strip():
                    st.error("Nombre y clave son obligatorios")
                else:
                    try:
                        client.create_kpi({
                            "clave": clave.strip(), "nombre": nombre.strip(),
                            "direccion": direccion, "unidad": unidad or None,
                            "meta": meta, "umbral_alerta": umbral,
                            "banda_min": banda_min, "banda_max": banda_max,
                        })
                        st.toast("KPI creado"); st.rerun()
                    except ApiError as e:
                        st.error(str(e))

    if data["kpis"]:
        with st.expander("📊 Registrar medición"):
            with st.form("nueva_medicion", clear_on_submit=True):
                opciones = {k["nombre"]: k["id"] for k in data["kpis"]}
                sel = st.selectbox("KPI", list(opciones.keys()))
                c1, c2, c3 = st.columns(3)
                fi = c1.date_input("Periodo inicio", value=date.today() - timedelta(days=6))
                ff = c2.date_input("Periodo fin", value=date.today())
                valor = c3.number_input("Valor", value=0.0)
                if st.form_submit_button("Registrar", type="primary"):
                    try:
                        client.add_measurement(opciones[sel], fi.isoformat(), ff.isoformat(), valor)
                        st.toast("Medición registrada"); st.rerun()
                    except ApiError as e:
                        st.error(str(e))
