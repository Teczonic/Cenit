"""Cockpit ejecutivo — la superficie diferencial de Cenit.

Responde las tres preguntas del líder: qué está en riesgo, qué está lento
y qué decisión tomar hoy. Combina el motor de flujo (aging, lead time real,
flow efficiency), el motor de riesgo y reglas de recomendación (aún sin IA:
esa llega cuando haya suficiente historial, per el plan).
"""

from __future__ import annotations

import streamlit as st

from domain.services import RiesgoService
from ui.api_client import ApiError
from ui.components import cargar_tareas, get_client, sidebar_filtros, tarjeta_tarea

NIVEL_EMOJI = {"crítico": "🔴", "alto": "🟠", "medio": "🟡", "bajo": "🟢"}
AGING_UMBRAL = 7  # días estancada en el mismo estado antes de alertar


def _atencion(tareas: list[dict], flow_por_tarea: dict) -> list[dict]:
    """Construye la lista priorizada 'qué requiere atención hoy' con decisión sugerida."""
    con_riesgo = {t["id"]: t for t in RiesgoService().ordenar_por_riesgo(tareas)}
    items: list[dict] = []
    vistas: set[int] = set()

    def agregar(t, motivo, decision, orden):
        if t["id"] in vistas:
            return
        vistas.add(t["id"])
        items.append({"tarea": t, "motivo": motivo, "decision": decision, "orden": orden})

    for t in tareas:
        if t.get("estado") == "Completado":
            continue
        tid = str(t["id"])
        flow = flow_por_tarea.get(tid, {})
        aging = flow.get("aging_days")
        riesgo = con_riesgo.get(t["id"])

        if riesgo and riesgo["nivel_riesgo"] in ("crítico", "alto"):
            agregar(t, f'Riesgo {riesgo["nivel_riesgo"]} (score {riesgo["score_normalizado"]})',
                    "Revisar hoy: mitigar, dividir o reasignar antes de que escale.", 0)
        elif aging is not None and aging >= AGING_UMBRAL:
            agregar(t, f"Estancada {aging:.0f} días en «{t['estado']}»",
                    "Desbloquear: identificar qué la detiene y quién la destraba.", 1)

    items.sort(key=lambda x: (x["orden"], -(x["tarea"].get("risk_score") or 0)))
    return items


def render():
    st.subheader("Cockpit del líder")
    st.caption("Qué está en riesgo · qué está lento · qué decidir hoy")

    tareas = sidebar_filtros(cargar_tareas())

    client = get_client()
    try:
        flow = client.analytics_flow()
    except ApiError as e:
        st.error(f"No se pudo cargar el motor de flujo: {e}")
        flow = {"por_tarea": {}, "lead_time_avg": None,
                "flow_efficiency_avg": None, "aging_avg": None}
    flow_por_tarea = flow.get("por_tarea", {})

    try:
        alignment = client.okr_overview().get("alignment_ratio")
    except ApiError:
        alignment = None

    abiertas = [t for t in tareas if t.get("estado") != "Completado"]
    con_riesgo = RiesgoService().ordenar_por_riesgo(tareas)
    en_riesgo = [t for t in con_riesgo if t["nivel_riesgo"] in ("crítico", "alto")]

    # ── Scorecard ejecutivo ──────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Tareas abiertas", len(abiertas))
    c2.metric("En riesgo", len(en_riesgo), delta_color="inverse")
    c3.metric("Lead time real (d)", flow.get("lead_time_avg") if flow.get("lead_time_avg") is not None else "—")
    c4.metric("Flow efficiency", f'{flow["flow_efficiency_avg"]:.0f}%' if flow.get("flow_efficiency_avg") is not None else "—")
    c5.metric("Aging prom. (d)", flow.get("aging_avg") if flow.get("aging_avg") is not None else "—",
              delta_color="inverse")
    c6.metric("Alineación OKR", f'{alignment:.0f}%' if alignment is not None else "—",
              help="Tareas abiertas conectadas a un key result")

    st.divider()

    # ── Qué requiere tu atención hoy ─────────────────────────────────────
    st.markdown("##### 🎯 Qué requiere tu atención hoy")
    atencion = _atencion(tareas, flow_por_tarea)
    if not atencion:
        st.success("Nada urgente en el radar. El flujo está sano.")
    else:
        for item in atencion[:12]:
            t = item["tarea"]
            with st.container(border=True):
                col_info, col_accion = st.columns([3, 2])
                with col_info:
                    st.markdown(f'**{t["descripcion"]}**')
                    meta = " · ".join(x for x in [
                        t.get("proyecto"), t.get("cliente"),
                        t.get("responsable") or "Sin asignar",
                    ] if x)
                    st.caption(f'{item["motivo"]} — {meta}')
                with col_accion:
                    st.markdown(f'💡 {item["decision"]}')

    st.divider()

    # ── Top de riesgo (detalle) ──────────────────────────────────────────
    st.markdown("##### ⚠️ Mayor riesgo abierto")
    if not en_riesgo:
        st.caption("Sin tareas de riesgo crítico o alto.")
    else:
        cols = st.columns(2)
        for i, t in enumerate(en_riesgo[:6]):
            with cols[i % 2]:
                tarjeta_tarea(t, key_prefix="cockpit_")
