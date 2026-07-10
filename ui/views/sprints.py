"""Sprints ligeros estilo Linear Cycles — compromiso, burndown, velocity y cierre.

El ciclo: planificar (comprometer tareas con puntos) → activar → seguir el
burndown → cerrar (velocity + Say/Do + carryover sugerido). El carryover nunca
se mueve solo: la lista es para que el líder decida.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.api_client import ApiError
from ui.components import cargar_tareas, get_client, recargar

ESTADO_SPRINT = {"planificado": "📝", "activo": "🟢", "cerrado": "✅", "cancelado": "⛔"}


def _form_nuevo_sprint():
    with st.expander("➕ Nuevo sprint"):
        with st.form("form_sprint"):
            c1, c2 = st.columns(2)
            with c1:
                nombre = st.text_input("Nombre *", placeholder="Sprint 2")
                entidad = st.selectbox("Entidad", ["Xertify", "Xertiflow"])
            with c2:
                fecha_inicio = st.date_input("Inicio")
                fecha_fin = st.date_input("Fin")
            objetivo = st.text_input("Objetivo del sprint (Sprint Goal)")
            if st.form_submit_button("Crear", type="primary"):
                if not nombre.strip():
                    st.error("El nombre es obligatorio")
                    st.stop()
                try:
                    get_client().create_sprint({
                        "nombre": nombre.strip(), "entidad": entidad,
                        "fecha_inicio": str(fecha_inicio), "fecha_fin": str(fecha_fin),
                        "objetivo": objetivo or None,
                    })
                    st.toast("Sprint creado")
                    st.session_state.pop("sprints", None)
                    st.rerun()
                except ApiError as e:
                    st.error(str(e))


def _seccion_compromiso(detalle: dict):
    """Agregar tareas al sprint. En planning comprometen; mid-sprint son churn."""
    tareas = cargar_tareas()
    ya = {t["task_id"] for t in detalle["tareas"] if not t.get("removed_at")}
    candidatas = [t for t in tareas
                  if t.get("entidad") == detalle["entidad"]
                  and t.get("estado") != "Completado" and t["id"] not in ya]
    if not candidatas:
        return
    opciones = {f'{t["descripcion"][:60]} ({t.get("story_points") or "sin pts"})': t["id"]
                for t in candidatas}
    sel = st.multiselect("Agregar tareas al sprint", list(opciones))
    if sel and st.button("Comprometer", type="primary"):
        try:
            res = get_client().add_sprint_tasks(detalle["id"], [opciones[s] for s in sel])
            if res.get("warning"):
                st.warning(res["warning"])
            if not res.get("committed"):
                st.info("El sprint ya está activo: estas tareas cuentan como churn (mid-sprint).")
            st.toast(f'{len(res.get("agregadas", []))} tarea(s) al sprint')
            st.rerun()
        except ApiError as e:
            if e.payload and e.payload.get("sin_puntos"):
                st.error(f'{e.payload["mensaje"]} (ids: {e.payload["sin_puntos"]})')
            else:
                st.error(str(e))


def _grafico_burndown(burndown: dict):
    serie = burndown.get("serie") or []
    if not serie:
        st.caption("Sin datos de burndown todavía (¿tareas sin puntos o sprint sin empezar?).")
        return
    df = pd.DataFrame(serie).set_index("fecha").rename(
        columns={"restante_real": "Real", "restante_ideal": "Ideal"})
    st.line_chart(df, height=240)
    alerta = burndown.get("alerta")
    desv = burndown.get("desviacion_actual")
    if alerta == "atraso":
        st.warning(f"Atraso de {desv} pts contra la línea ideal.")
    elif alerta == "adelanto":
        st.success(f"Adelanto de {abs(desv)} pts contra la línea ideal.")


def render():
    st.subheader("Sprints")
    st.caption("Compromiso · burndown · velocity · cierre con carryover")

    try:
        sprints = get_client().sprints()
    except ApiError as e:
        st.error(f"No se pudieron cargar los sprints: {e}")
        return

    _form_nuevo_sprint()
    if not sprints:
        st.info("Aún no hay sprints. Crea el primero arriba.")
        return

    activos_primero = sorted(sprints, key=lambda s: (s["estado"] != "activo",))
    etiquetas = {f'{ESTADO_SPRINT.get(s["estado"], "")} {s["nombre"]} · {s["entidad"]}': s["id"]
                 for s in activos_primero}
    sel = st.selectbox("Sprint", list(etiquetas), label_visibility="collapsed")
    detalle = get_client().sprint_detail(etiquetas[sel])

    if detalle.get("objetivo"):
        st.markdown(f'🎯 **{detalle["objetivo"]}**')
    vel = detalle["velocity"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Estado", detalle["estado"])
    c2.metric("Comprometidos", f'{vel["puntos_comprometidos"]} pts')
    c3.metric("Completados", f'{vel["puntos_completados"]} pts')
    c4.metric("Say/Do", f'{vel["say_do_ratio"]:.0f}%' if vel["say_do_ratio"] is not None else "—")
    c5.metric("Churn", f'{vel["churn_pct"]:.0f}%' if vel["churn_pct"] is not None else "—")

    st.markdown("##### 🔥 Burndown")
    _grafico_burndown(detalle["burndown"])

    # ── Tareas del sprint ────────────────────────────────────────────────
    st.markdown("##### Tareas del sprint")
    visibles = [t for t in detalle["tareas"] if not t.get("removed_at")]
    if not visibles:
        st.caption("Sin tareas comprometidas todavía.")
    for it in visibles:
        t = it.get("tarea") or {}
        c1, c2 = st.columns([6, 1])
        with c1:
            check = "✅" if t.get("estado") == "Completado" else ("🔄" if it["committed"] else "➕")
            churn = "" if it["committed"] else " · churn"
            st.markdown(f'{check} {t.get("descripcion", f"Tarea {it['task_id']}")} — '
                        f'**{it.get("points_snapshot") or "?"} pts**{churn} · '
                        f'{t.get("responsable") or "Sin asignar"}')
        with c2:
            if detalle["estado"] != "cerrado" and st.button(
                    "Quitar", key=f'sp_rm_{it["task_id"]}'):
                get_client().remove_sprint_task(detalle["id"], it["task_id"])
                st.rerun()

    if detalle["estado"] != "cerrado":
        _seccion_compromiso(detalle)

    # ── Acciones de ciclo ────────────────────────────────────────────────
    st.divider()
    ca, cb = st.columns(2)
    with ca:
        if detalle["estado"] == "planificado" and st.button("▶️ Activar sprint", type="primary"):
            try:
                get_client().patch_sprint(detalle["id"], {"estado": "activo"})
                st.rerun()
            except ApiError as e:
                st.error(str(e))
    with cb:
        if detalle["estado"] == "activo" and st.button("🏁 Cerrar sprint"):
            try:
                reporte = get_client().close_sprint(detalle["id"])
                st.session_state["ultimo_cierre"] = reporte
                st.rerun()
            except ApiError as e:
                st.error(str(e))

    if st.session_state.get("ultimo_cierre"):
        r = st.session_state.pop("ultimo_cierre")
        st.success(f'Sprint cerrado — velocity {r["puntos_completados"]} pts, '
                   f'Say/Do {r["say_do_ratio"] or 0}%.')
        if r["carryover_sugerido"]:
            st.warning("Carryover sugerido (tú decides a dónde van):")
            for c in r["carryover_sugerido"]:
                st.markdown(f'- {c["descripcion"]} ({c["story_points"] or "?"} pts)')

    # ── Histórico ────────────────────────────────────────────────────────
    st.divider()
    st.markdown("##### 📈 Velocity histórica")
    hist = get_client().analytics_velocity()
    if not hist["reportes"]:
        st.caption("Se calcula al cerrar sprints — la predictibilidad necesita historia.")
    else:
        h1, h2, h3 = st.columns(3)
        h1.metric("Sprints cerrados", hist["sprints"])
        h2.metric("Velocity promedio (últ. 3)", hist["velocity_promedio_3"] or "—")
        h3.metric("Say/Do promedio", f'{hist["say_do_promedio"]:.0f}%'
                  if hist["say_do_promedio"] is not None else "—")
        df = pd.DataFrame([{"sprint": r["nombre"], "velocity": r["puntos_completados"]}
                           for r in hist["reportes"]]).set_index("sprint")
        st.bar_chart(df, height=200)
