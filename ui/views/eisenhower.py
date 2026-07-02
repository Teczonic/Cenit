"""Matriz de Eisenhower — cuadrícula 2×2 (port de EisenhowerMatrix.tsx)."""

import streamlit as st

from domain.services import EIS_LABELS, EisenhowerService
from ui.components import cargar_tareas, sidebar_filtros, tarjeta_tarea


def render():
    st.subheader("Matriz de Eisenhower")
    st.caption("Importante vs urgente — solo tareas no completadas")

    tareas = sidebar_filtros(cargar_tareas())
    quads = EisenhowerService().agrupar_en_cuadrantes(tareas)

    for fila in (("Q1", "Q2"), ("Q3", "Q4")):
        cols = st.columns(2)
        for col, q in zip(cols, fila):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{EIS_LABELS[q]}** · {len(quads[q])}")
                    if not quads[q]:
                        st.caption("Sin tareas en este cuadrante.")
                    for t in quads[q]:
                        tarjeta_tarea(t, key_prefix=f"eis_{q}_")
