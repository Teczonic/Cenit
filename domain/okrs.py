"""Capa de dirección: cálculo de progreso de OKRs y alineación (puro, testeable).

Opera sobre dicts, igual que el resto del dominio. El progreso de un key result
es la fracción recorrida entre su valor inicial y su meta; el de un objective es
el promedio de sus KRs; el alignment ratio mide cuánto del trabajo abierto está
conectado a un resultado.
"""

from __future__ import annotations

from typing import Iterable


class OkrService:
    def progreso_kr(self, kr: dict) -> float:
        """Fracción 0..1 recorrida entre valor_inicial y valor_meta."""
        ini = kr.get("valor_inicial", 0) or 0
        meta = kr.get("valor_meta", 0) or 0
        act = kr.get("valor_actual", 0) or 0
        if meta == ini:
            return 1.0 if act >= meta else 0.0
        p = (act - ini) / (meta - ini)
        return max(0.0, min(1.0, round(p, 4)))

    def progreso_objective(self, krs: list[dict]) -> float:
        """Promedio del progreso de los KRs (0 si el objective no tiene ninguno)."""
        if not krs:
            return 0.0
        return round(sum(self.progreso_kr(k) for k in krs) / len(krs), 4)

    def alignment_ratio(self, tareas: list[dict], tareas_vinculadas: Iterable[int]) -> float:
        """% de tareas abiertas conectadas a algún key result."""
        vinculadas = set(tareas_vinculadas)
        abiertas = [t for t in tareas if t.get("estado") != "Completado"]
        if not abiertas:
            return 0.0
        con_kr = [t for t in abiertas if t.get("id") in vinculadas]
        return round(len(con_kr) / len(abiertas) * 100, 1)
