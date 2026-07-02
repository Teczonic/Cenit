"""Mi día — tareas propias agrupadas por urgencia (port de MiDia.tsx)."""

from datetime import datetime

import streamlit as st

from ui.components import cargar_tareas, tarjeta_tarea


def _dias_restantes(fecha_iso: str) -> int:
    f = datetime.fromisoformat(str(fecha_iso).replace("Z", "+00:00")).date()
    return (f - datetime.now(f_tz(fecha_iso)).date()).days


def f_tz(fecha_iso):
    return datetime.fromisoformat(str(fecha_iso).replace("Z", "+00:00")).tzinfo


def _es_hoy(fecha_iso) -> bool:
    if not fecha_iso:
        return False
    f = datetime.fromisoformat(str(fecha_iso).replace("Z", "+00:00"))
    return f.date() == datetime.now(f.tzinfo).date()


def _saludo() -> str:
    h = datetime.now().hour
    if h < 12:
        return "Buenos días"
    if h < 19:
        return "Buenas tardes"
    return "Buenas noches"


_DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
_MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
          "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _fecha_es(dt: datetime) -> str:
    return f"{_DIAS[dt.weekday()].capitalize()} {dt.day} de {_MESES[dt.month - 1]}"


def render():
    user = st.session_state.user
    tareas = cargar_tareas()
    mias = [t for t in tareas if t.get("responsable") == user["name"]]
    pendientes = [t for t in mias if t.get("estado") != "Completado"]
    completadas_hoy = sum(1 for t in mias if _es_hoy(t.get("fecha_completado")))

    st.subheader(f'{_saludo()}, {user["name"]}')
    st.caption(
        f'{_fecha_es(datetime.now())} · '
        f'{len(pendientes)} pendientes · {completadas_hoy} completadas hoy'
    )

    usadas: set[int] = set()

    def tomar(pred):
        r = [t for t in pendientes if t["id"] not in usadas and pred(t)]
        usadas.update(t["id"] for t in r)
        return r

    secciones = [
        ("🔴 Vencidas", "Nada vencido. Bien ahí.",
         tomar(lambda t: t.get("fecha_fin") and _dias_restantes(t["fecha_fin"]) < 0)),
        ("📅 Para hoy", "Sin entregas para hoy.",
         tomar(lambda t: t.get("fecha_fin") and _dias_restantes(t["fecha_fin"]) == 0)),
        ("⚡ Próximas (3 días)", "Nada vence en los próximos 3 días.",
         tomar(lambda t: t.get("fecha_fin") and _dias_restantes(t["fecha_fin"]) <= 3)),
        ("🎯 En curso / urgentes", "Sin tareas en proceso.",
         tomar(lambda t: t.get("estado") == "En Proceso" or t.get("prioridad") == "Urgente")),
    ]

    if not mias:
        st.info("No tienes tareas asignadas. 🎉")
        return

    for titulo, vacio, ts in secciones:
        st.markdown(f"##### {titulo} · {len(ts)}")
        if not ts:
            st.caption(vacio)
            continue
        cols = st.columns(2)
        for i, t in enumerate(ts):
            with cols[i % 2]:
                tarjeta_tarea(t, key_prefix="midia_")
