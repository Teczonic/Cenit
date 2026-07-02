"""Entidades del dominio de Cenit (portadas de src/domain/entities/*.ts)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import sqrt
from typing import Literal, Optional

Prioridad = Literal["Urgente", "Alta", "Media", "Baja"]
Estado = Literal["No Iniciado", "En Proceso", "Pausado", "Completado"]
Entidad = Literal["Xertify", "Xertiflow"]
Cuadrante = Literal["Q1", "Q2", "Q3", "Q4"]
NivelRiesgo = Literal["crítico", "alto", "medio", "bajo"]

PRIORIDADES: list[str] = ["Urgente", "Alta", "Media", "Baja"]
ESTADOS: list[str] = ["No Iniciado", "En Proceso", "Pausado", "Completado"]
ENTIDADES: list[str] = ["Xertify", "Xertiflow"]
PROYECTOS: list[str] = [
    "Operaciones", "Desarrollo", "Generador", "Soporte",
    "Marketing", "Wallet", "Scrapi", "Comercial",
]


class RiskScore:
    """Score de riesgo = probabilidad × impacto × (1 − cobertura de tests)."""

    def __init__(self, probabilidad: float, impacto: float, cobertura_test: float):
        self.probabilidad = probabilidad
        self.impacto = impacto
        self.cobertura_test = cobertura_test

    def calcular(self) -> float:
        return self.probabilidad * self.impacto * (1 - self.cobertura_test)

    def nivel(self) -> NivelRiesgo:
        s = self.calcular()
        if s >= 0.5:
            return "crítico"
        if s >= 0.3:
            return "alto"
        if s >= 0.15:
            return "medio"
        return "bajo"

    @staticmethod
    def from_raw_score(raw: float) -> "RiskScore":
        """Convierte un score crudo 0-100 (el que expone la API) a la escala 0-1."""
        normalized = min(raw / 100, 1)
        prob = sqrt(normalized)
        imp = sqrt(normalized)
        return RiskScore(prob, imp, 0)


@dataclass
class Usuario:
    id: int
    username: str
    nombre: str
    rol: str = "member"
    color: str = "#2563EB"

    @property
    def es_admin(self) -> bool:
        return self.rol == "admin"


@dataclass
class Tarea:
    id: int
    descripcion: str
    entidad: str
    proyecto: Optional[str] = None
    cliente: Optional[str] = None
    responsable: Optional[str] = None
    prioridad: str = "Media"
    estado: str = "No Iniciado"
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    comentarios: Optional[str] = None
    risk_score: float = 0

    def mover_estado(self, nuevo_estado: str) -> None:
        self.estado = nuevo_estado

    def calcular_riesgo(self) -> RiskScore:
        return RiskScore.from_raw_score(self.risk_score)

    def esta_vencida(self) -> bool:
        if not self.fecha_fin or self.estado == "Completado":
            return False
        return self.fecha_fin < datetime.now(self.fecha_fin.tzinfo)

    def asignar_responsable(self, usuario: Usuario) -> None:
        self.responsable = usuario.nombre
