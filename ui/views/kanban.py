"""Tablero Kanban — 4 columnas por estado (port de KanbanBoard.tsx)."""

import streamlit as st

from domain.services import ESTADO_COLORS, ESTADOS, KanbanService
from ui.components import cargar_tareas, dialogo_tarea, sidebar_filtros, tarjeta_tarea


def render():
    col_titulo, col_btn = st.columns([5, 1])
    with col_titulo:
        st.subheader("Kanban")
    with col_btn:
        if st.button("＋ Nueva tarea", type="primary", use_container_width=True):
            dialogo_tarea(None)

    tareas = sidebar_filtros(cargar_tareas())
    columnas = KanbanService().agrupar_por_estado(tareas)

    cols = st.columns(len(ESTADOS))
    for col, estado in zip(cols, ESTADOS):
        with col:
            color = ESTADO_COLORS[estado]
            st.markdown(
                f'<div style="border-top:3px solid {color};padding-top:6px;font-weight:600">'
                f'{estado} · {len(columnas[estado])}</div>',
                unsafe_allow_html=True,
            )
            for t in columnas[estado]:
                tarjeta_tarea(t, key_prefix="kb_")
