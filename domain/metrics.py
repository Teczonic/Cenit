"""Motor de métricas / KPIs — evaluación de semáforo y tendencia (puro, testeable).

Una métrica es un dato, no un módulo: aquí vive la lógica de evaluar un valor
contra su definición (meta, umbral, dirección) y devolver verde/ámbar/rojo, más
la tendencia entre snapshots. KPIs, DORA, OKR y SPACE reutilizan esto sin duplicar.
"""

from __future__ import annotations

from typing import Optional

ESTADOS = ("verde", "ambar", "rojo", "sin_datos")


def evaluar_estado(definicion: dict, valor: Optional[float]) -> str:
    """Aplica dirección + meta/umbral/banda → semáforo.

    - 'up'   (más es mejor): verde ≥ meta · rojo < umbral · ámbar entre medias.
    - 'down' (menos es mejor): verde ≤ meta · rojo > umbral · ámbar entre medias.
    - 'band' (rango objetivo): verde dentro de [banda_min, banda_max] · rojo fuera.
    """
    if valor is None:
        return "sin_datos"

    direccion = definicion.get("direccion")

    if direccion == "band":
        lo, hi = definicion.get("banda_min"), definicion.get("banda_max")
        if lo is None or hi is None:
            return "sin_datos"
        return "verde" if lo <= valor <= hi else "rojo"

    meta = definicion.get("meta")
    umbral = definicion.get("umbral_alerta")
    if meta is None:
        return "sin_datos"

    if direccion == "up":
        if valor >= meta:
            return "verde"
        if umbral is not None and valor < umbral:
            return "rojo"
        return "ambar"

    if direccion == "down":
        if valor <= meta:
            return "verde"
        if umbral is not None and valor > umbral:
            return "rojo"
        return "ambar"

    return "sin_datos"


def tendencia(snapshots: list[dict]) -> Optional[str]:
    """Compara los dos últimos snapshots (ordenados por periodo).

    Devuelve 'sube' | 'baja' | 'estable', o None si no hay suficientes datos.
    Es direccional en bruto — no sabe si subir es bueno; eso lo decide el semáforo.
    """
    if len(snapshots) < 2:
        return None
    ordenados = sorted(snapshots, key=lambda s: (s["periodo_inicio"], s["periodo_fin"]))
    delta = ordenados[-1]["valor"] - ordenados[-2]["valor"]
    if abs(delta) < 1e-9:
        return "estable"
    return "sube" if delta > 0 else "baja"


class MetricsEngine:
    """Fachada del motor. Hoy centraliza evaluación y tendencia; mañana registra
    providers (flow, okr, dora) que auto-calculan el valor desde datos de origen."""

    def evaluar(self, definicion: dict, valor: Optional[float]) -> str:
        return evaluar_estado(definicion, valor)

    def resumir(self, definicion: dict, snapshots: list[dict]) -> dict:
        ultimo = None
        if snapshots:
            ultimo = sorted(snapshots, key=lambda s: (s["periodo_inicio"], s["periodo_fin"]))[-1]
        valor = ultimo["valor"] if ultimo else None
        return {
            **definicion,
            "valor_actual": valor,
            "estado": self.evaluar(definicion, valor),
            "tendencia": tendencia(snapshots),
            "historial": [
                {"periodo_fin": str(s["periodo_fin"]), "valor": s["valor"], "estado": s["estado"]}
                for s in sorted(snapshots, key=lambda s: (s["periodo_inicio"], s["periodo_fin"]))
            ],
        }
