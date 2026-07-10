"""Tablero Kanban — 4 columnas por estado con límites WIP explícitos.

El WIP se mide sobre el tablero completo (no sobre la vista filtrada): el
límite es una propiedad del sistema, no de lo que estés mirando. El semáforo
del encabezado (normal / ámbar / rojo) es la práctica 2 de Kanban hecha visible.
"""

import streamlit as st

from domain.services import ESTADO_COLORS, ESTADOS, KanbanService, WipService
from ui.api_client import ApiError
from ui.components import cargar_tareas, dialogo_tarea, get_client, sidebar_filtros, tarjeta_tarea

WIP_STATUS_COLOR = {"al_limite": "#D97706", "excedido": "#DC2626"}


def _cargar_columnas() -> list[dict]:
    if "kanban_columns" not in st.session_state:
        try:
            st.session_state.kanban_columns = get_client().kanban_columns()
        except ApiError:
            st.session_state.kanban_columns = []
    return st.session_state.kanban_columns


def _panel_admin(columnas_cfg: list[dict]):
    """Editar límites WIP y políticas por columna (solo admins)."""
    with st.expander("⚙️ Límites WIP y políticas"):
        with st.form("wip_form"):
            nuevos: dict[str, tuple[int, str]] = {}
            for c in columnas_cfg:
                c1, c2 = st.columns([1, 3])
                with c1:
                    lim = st.number_input(
                        f'Límite · {c["estado"]}', min_value=0, step=1,
                        value=int(c.get("wip_limit") or 0),
                        help="0 = sin límite", key=f'wiplim_{c["estado"]}',
                    )
                with c2:
                    pol = st.text_input(
                        f'Política · {c["estado"]}',
                        value=c.get("policy_text") or "", key=f'wippol_{c["estado"]}',
                    )
                nuevos[c["estado"]] = (int(lim), pol)
            if st.form_submit_button("Guardar", type="primary"):
                try:
                    for estado, (lim, pol) in nuevos.items():
                        get_client().update_kanban_column(
                            estado, wip_limit=lim or None, policy_text=pol,
                        )
                    st.session_state.pop("kanban_columns", None)
                    st.toast("Límites actualizados")
                    st.rerun()
                except ApiError as e:
                    st.error(str(e))


def render():
    col_titulo, col_btn = st.columns([5, 1])
    with col_titulo:
        st.subheader("Kanban")
    with col_btn:
        if st.button("＋ Nueva tarea", type="primary", use_container_width=True):
            dialogo_tarea(None)

    todas = cargar_tareas()
    tareas = sidebar_filtros(todas)
    columnas_cfg = _cargar_columnas()
    wip = WipService().ocupacion(todas, columnas_cfg) if columnas_cfg else {}
    cfg_por_estado = {c["estado"]: c for c in columnas_cfg}

    columnas = KanbanService().agrupar_por_estado(tareas)

    cols = st.columns(len(ESTADOS))
    for col, estado in zip(cols, ESTADOS):
        with col:
            info = wip.get(estado, {})
            limite = info.get("wip_limit")
            status = info.get("status", "sin_limite")
            color = WIP_STATUS_COLOR.get(status, ESTADO_COLORS[estado])

            titulo = f"{estado} · {len(columnas[estado])}"
            if limite is not None:
                icono = " ⚠️" if status == "excedido" else ""
                titulo += (
                    f' <span style="color:{color};font-size:12px">'
                    f'WIP {info["ocupacion"]}/{limite}{icono}</span>'
                )
            st.markdown(
                f'<div style="border-top:3px solid {color};padding-top:6px;font-weight:600">'
                f'{titulo}</div>',
                unsafe_allow_html=True,
            )
            policy = cfg_por_estado.get(estado, {}).get("policy_text")
            if policy:
                st.caption(policy)
            for t in columnas[estado]:
                tarjeta_tarea(t, key_prefix="kb_")

    if st.session_state.get("user", {}).get("role") == "admin" and columnas_cfg:
        st.divider()
        _panel_admin(columnas_cfg)
