"""Importar CSV (Fase 1.5) — habilita la demo diagnóstico con datos reales.

El líder sube el export de Jira/Trello/Excel; Cenit detecta las columnas,
muestra una previsualización normalizada y, al confirmar, crea las tareas
vía la API. Sobre esos datos el Cockpit produce el diagnóstico inmediato.
"""

from __future__ import annotations

import csv
import io

import pandas as pd
import streamlit as st

from domain.csv_import import parse_tasks
from ui.api_client import ApiError
from ui.components import get_client, recargar


def _leer_filas(archivo) -> list[dict]:
    contenido = archivo.getvalue().decode("utf-8-sig", errors="replace")
    # Detecta el separador (Cenit usa ';', muchos exports usan ',')
    muestra = contenido[:2048]
    try:
        dialect = csv.Sniffer().sniff(muestra, delimiters=";,\t")
        sep = dialect.delimiter
    except csv.Error:
        sep = ";" if muestra.count(";") > muestra.count(",") else ","
    reader = csv.DictReader(io.StringIO(contenido), delimiter=sep)
    return [dict(r) for r in reader]


def render():
    st.subheader("Importar tareas desde CSV")
    st.caption("Sube tu export de Jira, Trello o Excel — Cenit detecta las columnas automáticamente")

    archivo = st.file_uploader("Archivo CSV", type=["csv"])
    if not archivo:
        st.info("Formatos soportados: encabezados en español o en inglés "
                "(Summary/Status/Priority/Assignee/Due Date, etc.). Separador ; , o tab.")
        return

    try:
        filas = _leer_filas(archivo)
    except Exception as e:  # noqa: BLE001 — feedback directo al usuario
        st.error(f"No se pudo leer el archivo: {e}")
        return

    resultado = parse_tasks(filas)

    for w in resultado.warnings:
        st.warning(w)
    if not resultado.tasks:
        return

    st.success(f"{len(resultado.tasks)} tareas reconocidas · {resultado.skipped} omitidas")
    with st.expander("Columnas detectadas"):
        st.json(resultado.mapping)

    st.markdown("##### Previsualización")
    st.dataframe(
        pd.DataFrame(resultado.tasks)[
            ["descripcion", "estado", "prioridad", "responsable", "cliente", "fecha_fin"]
        ],
        use_container_width=True, hide_index=True,
    )

    if st.button(f"Importar {len(resultado.tasks)} tareas", type="primary"):
        client = get_client()
        creadas, errores = 0, 0
        barra = st.progress(0.0)
        for i, data in enumerate(resultado.tasks):
            try:
                client.create_task(data)
                creadas += 1
            except ApiError:
                errores += 1
            barra.progress((i + 1) / len(resultado.tasks))
        st.toast(f"{creadas} tareas importadas" + (f" · {errores} con error" if errores else ""))
        if creadas:
            st.session_state.pop("tareas", None)
            st.success(f"Listo. Abre el Cockpit para ver el diagnóstico de las {creadas} tareas.")
