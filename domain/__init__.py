"""Dominio de Cenit — entidades y servicios de negocio en Python puro.

Este paquete no depende de FastAPI ni de Streamlit: es la capa que
puede testearse con pytest sin levantar nada.
"""

from .entities import RiskScore, Tarea, Usuario
from .metrics import MetricsEngine, evaluar_estado, tendencia
from .okrs import OkrService
from .sprints import SprintService
from .services import (
    AnalyticsService,
    EisenhowerService,
    FiltroService,
    FlowService,
    KanbanService,
    RiesgoService,
    WipService,
)

__all__ = [
    "RiskScore",
    "Tarea",
    "Usuario",
    "AnalyticsService",
    "EisenhowerService",
    "FiltroService",
    "FlowService",
    "KanbanService",
    "MetricsEngine",
    "OkrService",
    "RiesgoService",
    "SprintService",
    "WipService",
    "evaluar_estado",
    "tendencia",
]
