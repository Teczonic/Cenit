"""Equipo — miembros, carga de trabajo y alta de usuarios (admin)."""

import pandas as pd
import streamlit as st

from domain.services import AnalyticsService
from ui.api_client import ApiError
from ui.components import cargar_tareas, cargar_usuarios, get_client


def render():
    st.subheader("Equipo")

    usuarios = cargar_usuarios()
    tareas = cargar_tareas()
    stats = {s["nombre"]: s for s in AnalyticsService().por_responsable(tareas)}

    filas = []
    for u in usuarios:
        s = stats.get(u["name"], {})
        filas.append({
            "Nombre": u["name"],
            "Usuario": u["username"],
            "Rol": "👑 admin" if u["role"] == "admin" else "member",
            "Tareas": s.get("total", 0),
            "Completadas": s.get("completadas", 0),
            "Pendientes": s.get("total", 0) - s.get("completadas", 0),
        })
    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

    if st.session_state.user.get("role") == "admin":
        st.markdown("##### Crear usuario")
        with st.form("nuevo_usuario", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                username = st.text_input("Username")
                name = st.text_input("Nombre completo")
            with c2:
                password = st.text_input("Contraseña", type="password")
                role = st.selectbox("Rol", ["member", "admin"])
                color = st.color_picker("Color", "#2563EB")
            if st.form_submit_button("Crear", type="primary"):
                if not username or not name or not password:
                    st.error("Todos los campos son obligatorios")
                else:
                    try:
                        get_client().create_user(username, name, password, role, color)
                        st.session_state.pop("usuarios", None)
                        st.toast(f"Usuario {username} creado")
                        st.rerun()
                    except ApiError as e:
                        st.error(str(e))
    else:
        st.caption("Solo los admins pueden crear usuarios.")
