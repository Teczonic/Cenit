"""Dashboard de analytics (port de AnalyticsDashboard.tsx) + capa Lean.

La pestaña Lean responde la pregunta que Trello/Jira no hacen: ¿cuánto del
tablero es trabajo real y cuánto es desperdicio (espera, bloqueos, zombis)?
"""

import pandas as pd
import streamlit as st

from domain.lean import WASTE_TYPES
from domain.services import AnalyticsService
from ui.api_client import ApiError
from ui.components import cargar_tareas, get_client


def render():
    st.subheader("Analytics")
    tab_general, tab_lean = st.tabs(["📊 General", "🧹 Lean / Desperdicio"])
    with tab_general:
        _tab_general()
    with tab_lean:
        _tab_lean()


def _tab_general():
    client = get_client()
    summary = client.analytics_summary()
    tareas = cargar_tareas()
    svc = AnalyticsService()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total tareas", summary["total"])
    c2.metric("En proceso", summary["en_proceso"])
    c3.metric("Completadas", summary["completadas"])
    c4.metric("Urgentes", summary["urgentes"], delta_color="inverse")
    c5.metric("Vencidas", summary["vencidas"], delta_color="inverse")
    st.metric("Lead time promedio (días)", summary["avg_lead_time"])

    col_izq, col_der = st.columns(2)

    with col_izq:
        st.markdown("##### Tareas por prioridad")
        por_prio = svc.por_prioridad(tareas)
        if por_prio:
            df = pd.DataFrame(
                {"prioridad": list(por_prio.keys()), "tareas": list(por_prio.values())}
            ).set_index("prioridad")
            st.bar_chart(df)

        st.markdown("##### Tareas por entidad")
        df_ent = pd.DataFrame(
            {"entidad": list(summary["by_entidad"].keys()),
             "tareas": list(summary["by_entidad"].values())}
        ).set_index("entidad")
        st.bar_chart(df_ent)

    with col_der:
        st.markdown("##### Throughput mensual (completadas)")
        throughput = svc.throughput_mensual(tareas)
        if throughput:
            df_th = pd.DataFrame(throughput).set_index("mes")
            st.bar_chart(df_th)
        else:
            st.caption("Aún no hay tareas completadas.")

        st.markdown("##### Lead time por persona")
        lead = client.analytics_lead_time()
        if lead:
            st.dataframe(
                pd.DataFrame(lead).rename(columns={
                    "responsable": "Responsable", "count": "Completadas",
                    "avg": "Promedio (d)", "min": "Mín (d)", "max": "Máx (d)",
                }),
                use_container_width=True, hide_index=True,
            )
        else:
            st.caption("Sin datos de lead time todavía.")

    st.markdown("##### Carga por responsable")
    por_resp = svc.por_responsable(tareas)
    if por_resp:
        df_resp = pd.DataFrame([
            {"Responsable": s["nombre"], "Total": s["total"],
             "Completadas": s["completadas"],
             "Lead time prom. (d)": round(s["avg_lead_time"], 1) if s["avg_lead_time"] else None}
            for s in por_resp
        ])
        st.dataframe(df_resp, use_container_width=True, hide_index=True)


def _tab_lean():
    """Desperdicio reportado + detectado, bloqueos activos, zombis y Little."""
    try:
        lean = get_client().analytics_lean()
    except ApiError as e:
        st.error(f"No se pudo cargar la capa Lean: {e}")
        return

    little = lean["little"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Flow efficiency", f'{lean["flow_efficiency_avg"]:.0f}%'
              if lean.get("flow_efficiency_avg") is not None else "—",
              help="% del tiempo en que las tareas estuvieron trabajándose vs esperando")
    c2.metric("Tasa de retrabajo", f'{lean["tasa_retrabajo"]}%', delta_color="inverse",
              help="Tareas reabiertas después de completadas")
    c3.metric("WIP actual", little["wip_actual"])
    c4.metric("Lead time esperado (Little)",
              f'{little["lead_time_esperado_dias"]} d'
              if little["lead_time_esperado_dias"] is not None else "—",
              help="WIP ÷ throughput semanal × 7 — si el medido es mucho menor, hay tareas zombi")

    col_izq, col_der = st.columns(2)

    with col_izq:
        st.markdown("##### Pareto de desperdicio")
        if lean["pareto"]:
            df = pd.DataFrame(lean["pareto"]).set_index("waste_type")
            st.bar_chart(df, height=220)
        else:
            st.caption("Sin desperdicio reportado ni detectado. Buen flujo.")

        st.markdown("##### 🧟 Tareas zombi (>14 días sin moverse)")
        if not lean["tareas_zombi"]:
            st.caption("Ninguna. El WIP está vivo.")
        for z in lean["tareas_zombi"][:8]:
            st.markdown(f'- **{z["descripcion"][:60]}** — {z["dias_sin_movimiento"]:.0f} días '
                        f'en «{z["estado"]}» · {z["responsable"] or "Sin asignar"}')

    with col_der:
        st.markdown("##### 🚧 Bloqueos activos")
        if not lean["bloqueos_activos"]:
            st.caption("Sin bloqueos abiertos.")
        for w in lean["bloqueos_activos"]:
            b1, b2 = st.columns([4, 1])
            with b1:
                st.markdown(f'**{w["waste_type"]}** — {w.get("descripcion") or "sin detalle"} '
                            f'(tarea {w["task_id"]})')
            with b2:
                if st.button("Resolver", key=f'waste_{w["id"]}'):
                    get_client().resolve_waste(w["id"])
                    st.rerun()

        st.markdown("##### Reportar bloqueo")
        tareas = [t for t in cargar_tareas() if t.get("estado") != "Completado"]
        opciones = {f'{t["descripcion"][:55]}': t["id"] for t in tareas}
        with st.form("form_waste"):
            sel = st.selectbox("Tarea", list(opciones)) if opciones else None
            tipo = st.selectbox("Tipo de desperdicio", WASTE_TYPES)
            desc = st.text_input("Descripción (qué lo bloquea)")
            if st.form_submit_button("Reportar") and sel:
                try:
                    get_client().report_waste(opciones[sel], tipo, desc or None)
                    st.toast("Bloqueo reportado")
                    st.rerun()
                except ApiError as e:
                    st.error(str(e))

    if lean["detecciones"]:
        st.divider()
        st.markdown("##### 🔍 Detección automática (la memoria histórica delata)")
        for d in lean["detecciones"][:10]:
            st.markdown(f'- `{d["waste_type"]}` — {d["detalle"]}')
