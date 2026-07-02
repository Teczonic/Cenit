"""Dashboard de analytics (port de AnalyticsDashboard.tsx)."""

import pandas as pd
import streamlit as st

from domain.services import AnalyticsService
from ui.components import cargar_tareas, get_client


def render():
    st.subheader("Analytics")

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
