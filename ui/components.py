"""Componentes compartidos de la UI Streamlit: tarjetas de tarea, formularios, filtros."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

import streamlit as st

from domain.entities import ENTIDADES, ESTADOS, PRIORIDADES, PROYECTOS
from domain.services import ESTADO_COLORS, PRIO_COLORS, FiltroService
from ui.api_client import ApiError, CenitClient


def get_client() -> CenitClient:
    return CenitClient(token=st.session_state.get("token"))


def cargar_tareas() -> list[dict]:
    if "tareas" not in st.session_state:
        st.session_state.tareas = get_client().get_tasks()
    return st.session_state.tareas


def cargar_usuarios() -> list[dict]:
    if "usuarios" not in st.session_state:
        st.session_state.usuarios = get_client().get_users()
    return st.session_state.usuarios


def recargar():
    st.session_state.pop("tareas", None)
    st.rerun()


def _fmt_fecha(iso: Optional[str]) -> str:
    if not iso:
        return "—"
    return str(iso)[:10]


def badge(texto: str, color: str) -> str:
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'border-radius:10px;padding:1px 8px;font-size:11px;white-space:nowrap">{texto}</span>'
    )


def tarjeta_tarea(t: dict, key_prefix: str = ""):
    """Tarjeta compacta de tarea con acciones de estado y edición."""
    prio_color = PRIO_COLORS.get(t.get("prioridad"), "#64748B")
    estado_color = ESTADO_COLORS.get(t.get("estado"), "#64748B")
    with st.container(border=True):
        st.markdown(
            f'{badge(t.get("prioridad", ""), prio_color)} '
            f'{badge(t.get("estado", ""), estado_color)} '
            f'{badge(t.get("entidad", ""), "#7C3AED")}',
            unsafe_allow_html=True,
        )
        st.markdown(f'**{t.get("descripcion", "")}**')
        meta = " · ".join(
            x for x in [
                t.get("proyecto"), t.get("cliente"), t.get("responsable"),
                f'vence {_fmt_fecha(t.get("fecha_fin"))}' if t.get("fecha_fin") else None,
            ] if x
        )
        if meta:
            st.caption(meta)

        col1, col2 = st.columns([3, 1])
        with col1:
            nuevo = st.selectbox(
                "Mover a", ESTADOS,
                index=ESTADOS.index(t["estado"]) if t.get("estado") in ESTADOS else 0,
                key=f"{key_prefix}estado_{t['id']}", label_visibility="collapsed",
            )
            if nuevo != t.get("estado"):
                try:
                    get_client().patch_status(t["id"], nuevo)
                    st.toast(f"Estado: {nuevo}")
                    recargar()
                except ApiError as e:
                    st.error(str(e))
        with col2:
            if st.button("Editar", key=f"{key_prefix}edit_{t['id']}", use_container_width=True):
                dialogo_tarea(t)


@st.dialog("Tarea", width="large")
def dialogo_tarea(tarea: Optional[dict] = None):
    """Formulario de creación/edición de tarea (equivalente al TaskModal)."""
    es_nueva = tarea is None
    t = tarea or {}
    usuarios = cargar_usuarios()
    nombres = [""] + [u["name"] for u in usuarios]

    with st.form("form_tarea"):
        descripcion = st.text_area("Descripción *", value=t.get("descripcion", ""))
        c1, c2, c3 = st.columns(3)
        with c1:
            entidad = st.selectbox("Entidad", ENTIDADES,
                                   index=ENTIDADES.index(t["entidad"]) if t.get("entidad") in ENTIDADES else 0)
            proyecto = st.selectbox("Proyecto", [""] + PROYECTOS,
                                    index=([""] + PROYECTOS).index(t["proyecto"]) if t.get("proyecto") in PROYECTOS else 0)
        with c2:
            prioridad = st.selectbox("Prioridad", PRIORIDADES,
                                     index=PRIORIDADES.index(t["prioridad"]) if t.get("prioridad") in PRIORIDADES else 2)
            estado = st.selectbox("Estado", ESTADOS,
                                  index=ESTADOS.index(t["estado"]) if t.get("estado") in ESTADOS else 0)
        with c3:
            responsable = st.selectbox("Responsable", nombres,
                                       index=nombres.index(t["responsable"]) if t.get("responsable") in nombres else 0)
            cliente = st.text_input("Cliente", value=t.get("cliente") or "")

        c4, c5 = st.columns(2)
        with c4:
            ff_actual = None
            if t.get("fecha_fin"):
                ff_actual = datetime.fromisoformat(str(t["fecha_fin"]).replace("Z", "+00:00")).date()
            fecha_fin = st.date_input("Fecha límite", value=ff_actual)
        with c5:
            comentarios = st.text_input("Comentarios", value=t.get("comentarios") or "")

        if st.form_submit_button("Guardar", type="primary", use_container_width=True):
            if not descripcion.strip():
                st.error("La descripción es obligatoria")
                st.stop()
            data = {
                "entidad": entidad,
                "proyecto": proyecto or None,
                "cliente": cliente or None,
                "descripcion": descripcion.strip(),
                "prioridad": prioridad,
                "estado": estado,
                "responsable": responsable or None,
                "comentarios": comentarios or None,
                "fecha_fin": (
                    datetime.combine(fecha_fin, datetime.min.time()).isoformat()
                    if isinstance(fecha_fin, date) else None
                ),
            }
            try:
                if es_nueva:
                    get_client().create_task(data)
                    st.toast("Tarea creada")
                else:
                    get_client().update_task(t["id"], data)
                    st.toast("Tarea actualizada")
                recargar()
            except ApiError as e:
                st.error(str(e))

    if not es_nueva:
        with st.expander("🕓 Historial de estados"):
            try:
                trans = get_client().task_transitions(t["id"])
            except ApiError:
                trans = []
            if not trans:
                st.caption("Sin transiciones registradas todavía.")
            for tr in trans:
                origen = tr.get("from_state") or "—"
                cuando = _fmt_fecha(tr.get("changed_at"))
                quien = tr.get("changed_by") or "sistema"
                st.markdown(f'`{cuando}` · {origen} → **{tr["to_state"]}** · {quien}')

    if not es_nueva and st.session_state.get("user", {}).get("role") == "admin":
        if st.button("🗑️ Eliminar tarea", type="secondary"):
            try:
                get_client().delete_task(t["id"])
                st.toast("Tarea eliminada")
                recargar()
            except ApiError as e:
                st.error(str(e))


def sidebar_filtros(tareas: list[dict]) -> list[dict]:
    """Filtros laterales compartidos (equivalente al FilterContext)."""
    usuarios = cargar_usuarios()
    with st.sidebar:
        st.divider()
        st.caption("Filtros")
        entidad = st.selectbox("Entidad", ["", *ENTIDADES], key="f_entidad")
        prioridad = st.selectbox("Prioridad", ["", *PRIORIDADES], key="f_prioridad")
        responsable = st.selectbox("Responsable", [""] + [u["name"] for u in usuarios], key="f_responsable")
        search = st.text_input("Buscar", key="f_search", placeholder="descripción o cliente…")

    return FiltroService().filtrar(
        tareas, entidad=entidad, prioridad=prioridad,
        responsable=responsable, search=search,
    )
