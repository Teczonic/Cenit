"""OKRs — capa de dirección: objetivos, key results y alineación del trabajo."""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from ui.api_client import ApiError
from ui.components import get_client


def render():
    st.subheader("OKRs — dirección del trimestre")
    st.caption("El puente entre el trabajo diario y los resultados. Vincula tareas a un KR para que cuenten.")

    client = get_client()
    try:
        cycles = client.okr_cycles()
    except ApiError as e:
        st.error(str(e))
        return

    if not cycles:
        st.info("Aún no hay ciclos de OKR.")
    else:
        nombres = [c["nombre"] for c in cycles]
        sel = st.selectbox("Ciclo", nombres, key="okr_cycle")
        cycle = next(c for c in cycles if c["nombre"] == sel)

        overview = client.okr_overview(cycle_id=cycle["id"])
        st.metric("Alineación del trabajo", f'{overview["alignment_ratio"]:.0f}%',
                  help="Porcentaje de tareas abiertas conectadas a algún key result")

        if not overview["objectives"]:
            st.caption("Este ciclo no tiene objetivos todavía.")
        for obj in overview["objectives"]:
            with st.container(border=True):
                cab, prog = st.columns([3, 1])
                with cab:
                    st.markdown(f'**{obj["titulo"]}**')
                    meta = " · ".join(x for x in [obj.get("entidad"), obj.get("owner")] if x)
                    if meta:
                        st.caption(meta)
                with prog:
                    st.metric("Progreso", f'{obj["progreso"] * 100:.0f}%')
                st.progress(obj["progreso"])

                for kr in obj["key_results"]:
                    u = f' {kr["unidad"]}' if kr.get("unidad") else ""
                    st.markdown(f'· {kr["titulo"]}  —  **{kr["valor_actual"]:g}{u}** / {kr["valor_meta"]:g}{u}')
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.progress(kr["progreso"])
                    with c2:
                        nuevo = st.number_input(
                            "Actualizar", value=float(kr["valor_actual"]),
                            key=f'kr_{kr["id"]}', label_visibility="collapsed",
                        )
                        if nuevo != kr["valor_actual"]:
                            try:
                                client.patch_kr(kr["id"], nuevo)
                                st.toast("KR actualizado")
                                st.rerun()
                            except ApiError as e:
                                st.error(str(e))

    st.divider()

    # ── Crear ──────────────────────────────────────────────────────────
    with st.expander("➕ Crear objetivo o key result"):
        if not cycles:
            st.caption("Primero crea un ciclo abajo.")
        else:
            with st.form("nuevo_objetivo", clear_on_submit=True):
                st.markdown("**Nuevo objetivo**")
                titulo = st.text_input("Título del objetivo")
                cyc = st.selectbox("Ciclo", [c["nombre"] for c in cycles], key="obj_cycle")
                if st.form_submit_button("Crear objetivo", type="primary"):
                    cid = next(c["id"] for c in cycles if c["nombre"] == cyc)
                    if titulo.strip():
                        client.create_objective(cid, titulo.strip())
                        st.toast("Objetivo creado"); st.rerun()
                    else:
                        st.error("El título es obligatorio")

            overview = client.okr_overview()
            if overview["objectives"]:
                with st.form("nuevo_kr", clear_on_submit=True):
                    st.markdown("**Nuevo key result**")
                    objs = {o["titulo"]: o["id"] for o in overview["objectives"]}
                    obj_sel = st.selectbox("Objetivo", list(objs.keys()))
                    kt = st.text_input("Título del key result")
                    a, b, c = st.columns(3)
                    vi = a.number_input("Inicial", value=0.0)
                    vm = b.number_input("Meta", value=100.0)
                    va = c.number_input("Actual", value=0.0)
                    unidad = st.text_input("Unidad (opcional)", placeholder="días, %, tareas…")
                    if st.form_submit_button("Crear key result", type="primary"):
                        if kt.strip():
                            client.create_key_result(objs[obj_sel], kt.strip(), vi, vm, va, unidad or None)
                            st.toast("Key result creado"); st.rerun()
                        else:
                            st.error("El título es obligatorio")

    with st.expander("➕ Crear ciclo de OKR"):
        with st.form("nuevo_ciclo", clear_on_submit=True):
            nombre = st.text_input("Nombre", placeholder="Q4 2026")
            ci, cf = st.columns(2)
            fi = ci.date_input("Inicio", value=date.today())
            ff = cf.date_input("Fin", value=date.today() + timedelta(days=90))
            if st.form_submit_button("Crear ciclo", type="primary"):
                if nombre.strip():
                    client.create_okr_cycle(nombre.strip(), fi.isoformat(), ff.isoformat())
                    st.toast("Ciclo creado"); st.rerun()
                else:
                    st.error("El nombre es obligatorio")
