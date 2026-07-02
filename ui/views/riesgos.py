"""Matriz de riesgos — top tareas por risk score (port de RiskMatrix.tsx)."""

import pandas as pd
import streamlit as st

from domain.services import RiesgoService
from ui.components import cargar_tareas, sidebar_filtros

NIVEL_EMOJI = {"crítico": "🔴", "alto": "🟠", "medio": "🟡", "bajo": "🟢"}


def render():
    st.subheader("Matriz de riesgos")
    st.caption("Score = probabilidad × impacto × (1 − cobertura de tests) · top 30 tareas abiertas")

    tareas = sidebar_filtros(cargar_tareas())
    con_riesgo = RiesgoService().ordenar_por_riesgo(tareas)

    if not con_riesgo:
        st.info("No hay tareas abiertas con score de riesgo.")
        return

    niveles = {}
    for t in con_riesgo:
        niveles[t["nivel_riesgo"]] = niveles.get(t["nivel_riesgo"], 0) + 1
    cols = st.columns(4)
    for col, nivel in zip(cols, ("crítico", "alto", "medio", "bajo")):
        col.metric(f'{NIVEL_EMOJI[nivel]} {nivel.capitalize()}', niveles.get(nivel, 0))

    df = pd.DataFrame([
        {
            "Nivel": f'{NIVEL_EMOJI[t["nivel_riesgo"]]} {t["nivel_riesgo"]}',
            "Score": t["score_normalizado"],
            "Descripción": t["descripcion"],
            "Proyecto": t.get("proyecto") or "—",
            "Cliente": t.get("cliente") or "—",
            "Responsable": t.get("responsable") or "Sin asignar",
            "Estado": t["estado"],
        }
        for t in con_riesgo
    ])
    st.dataframe(
        df, use_container_width=True, hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score", format="%.1f", min_value=0,
                max_value=max(float(df["Score"].max()), 1.0),
            ),
        },
    )
