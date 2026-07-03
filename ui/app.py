"""Cenit — Team Backlog Manager. UI en Streamlit, 100% Python.

Ejecutar:  streamlit run ui/app.py
Requiere la API FastAPI corriendo (uvicorn api.main:app) y CENIT_API_URL apuntando a ella.
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.api_client import ApiError, CenitClient  # noqa: E402
from ui.views import (  # noqa: E402
    analytics, cockpit, eisenhower, equipo, importar, kanban, mi_dia, okrs, riesgos,
)

st.set_page_config(page_title="Cenit", page_icon="🏔️", layout="wide")


def pantalla_login():
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        st.title("🏔️ Cenit")
        st.caption("Team Backlog Manager — Xertify / Xertiflow")
        with st.form("login"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                try:
                    data = CenitClient().login(username, password)
                    st.session_state.token = data["token"]
                    st.session_state.user = data["user"]
                    st.rerun()
                except ApiError as e:
                    st.error(str(e))


def app():
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f'### 🏔️ Cenit')
        st.markdown(
            f'<span style="background:{user.get("color", "#2563EB")};color:#fff;'
            f'border-radius:50%;padding:4px 9px;font-size:12px">'
            f'{user["name"][:1]}</span>  **{user["name"]}** · {user["role"]}',
            unsafe_allow_html=True,
        )
        if st.button("Recargar datos", use_container_width=True):
            st.session_state.pop("tareas", None)
            st.session_state.pop("usuarios", None)
            st.rerun()
        if st.button("Cerrar sesión", use_container_width=True):
            for k in ("token", "user", "tareas", "usuarios"):
                st.session_state.pop(k, None)
            st.rerun()

    paginas = st.navigation({
        "Dirigir": [
            st.Page(cockpit.render, title="Cockpit", icon="🧭", url_path="cockpit", default=True),
            st.Page(mi_dia.render, title="Mi día", icon="🌅", url_path="mi-dia"),
            st.Page(okrs.render, title="OKRs", icon="🎯", url_path="okrs"),
        ],
        "Operar": [
            st.Page(kanban.render, title="Kanban", icon="📋", url_path="kanban"),
            st.Page(eisenhower.render, title="Eisenhower", icon="🎯", url_path="eisenhower"),
            st.Page(riesgos.render, title="Riesgos", icon="⚠️", url_path="riesgos"),
        ],
        "Analizar": [
            st.Page(analytics.render, title="Analytics", icon="📊", url_path="analytics"),
            st.Page(equipo.render, title="Equipo", icon="👥", url_path="equipo"),
        ],
        "Datos": [
            st.Page(importar.render, title="Importar CSV", icon="📥", url_path="importar"),
        ],
    })

    try:
        paginas.run()
    except ApiError as e:
        st.error(f"Error de API: {e}")
        if "401" in str(e):
            for k in ("token", "user"):
                st.session_state.pop(k, None)
            st.rerun()


if "token" not in st.session_state:
    pantalla_login()
else:
    app()
