import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def make_raw(**overrides) -> dict:
    """Tarea cruda tal como la devuelve la API (equivalente al makeRaw de Vitest)."""
    base = {
        "id": 1,
        "entidad": "Xertify",
        "proyecto": "Desarrollo",
        "cliente": None,
        "descripcion": "Test",
        "prioridad": "Media",
        "estado": "No Iniciado",
        "responsable": None,
        "comentarios": None,
        "fecha_inicio": None,
        "fecha_fin": None,
        "fecha_completado": None,
        "lead_time_days": None,
        "eisenhower": None,
        "risk_score": None,
        "created_by": None,
        "created_at": "",
        "updated_at": "",
    }
    base.update(overrides)
    return base


@pytest.fixture()
def raw_factory():
    return make_raw
