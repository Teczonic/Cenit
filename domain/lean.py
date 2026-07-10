"""Capa Lean sobre el historial de transiciones — desperdicio, bloqueos y flujo.

La pregunta que Lean invierte: no «¿está todo el mundo ocupado?» sino «¿cuánto
del lead time fue trabajo real y cuánto espera?». Opera sobre dicts (tareas,
transiciones, waste_events), sin base de datos — testeable en aislamiento.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

# Los 7 desperdicios (mudas) del software lean — Poppendieck
WASTE_TYPES = ("espera", "handoff", "retrabajo", "multitasking",
               "sobreproceso", "defecto", "trabajo_parcial")

UMBRAL_ZOMBI_DIAS = 14        # WIP sin transición en >14 días = inventario muerto
UMBRAL_PAUSA_DIAS = 7         # Pausado >7 días sin bloqueo reportado = trabajo parcial
UMBRAL_MULTITASKING = 3       # >3 tareas En Proceso por persona = desperdicio de movimiento
ESTADOS_WIP = ("En Proceso", "Pausado")


def _dias(desde: Optional[datetime], hasta: datetime) -> Optional[float]:
    if not desde:
        return None
    return round((hasta - desde).total_seconds() / 86400, 1)


class LeanService:
    """Detección de desperdicio (reportado + automático), retrabajo,
    tareas zombi y Ley de Little sobre la memoria histórica de Cenit."""

    def tasa_retrabajo(self, transiciones: list[dict]) -> float:
        """% de tareas reabiertas: transiciones que salen de «Completado»."""
        reabiertas = sum(1 for t in transiciones if t.get("from_state") == "Completado")
        completadas = sum(1 for t in transiciones if t.get("to_state") == "Completado")
        return round(reabiertas / completadas * 100, 1) if completadas else 0.0

    def _ultima_transicion(self, transiciones: list[dict]) -> dict[int, datetime]:
        ultima: dict[int, datetime] = {}
        for t in transiciones:
            tid, cuando = t["task_id"], t["changed_at"]
            if tid not in ultima or cuando > ultima[tid]:
                ultima[tid] = cuando
        return ultima

    def tareas_zombi(self, tareas: list[dict], transiciones: list[dict],
                     ahora: datetime) -> list[dict]:
        """WIP sin movimiento en >14 días: inventario que infla la Ley de Little."""
        ultima = self._ultima_transicion(transiciones)
        zombis = []
        for t in tareas:
            if t.get("estado") not in ESTADOS_WIP:
                continue
            desde = ultima.get(t["id"])
            dias = _dias(desde, ahora)
            if dias is not None and dias > UMBRAL_ZOMBI_DIAS:
                zombis.append({"id": t["id"], "descripcion": t.get("descripcion"),
                               "responsable": t.get("responsable"),
                               "estado": t.get("estado"), "dias_sin_movimiento": dias})
        return sorted(zombis, key=lambda z: -z["dias_sin_movimiento"])

    def detectar_desperdicio(self, tareas: list[dict], waste_events: list[dict],
                             transiciones: list[dict], ahora: datetime) -> dict:
        """Pareto de desperdicio: eventos reportados + detecciones automáticas.

        Automáticas (sin que nadie reporte nada — la memoria histórica delata):
        - multitasking: responsable con >3 tareas En Proceso
        - trabajo_parcial: Pausado >7 días sin bloqueo reportado activo
        - retrabajo: transiciones Completado → otro estado
        """
        detecciones: list[dict] = []

        # multitasking
        en_proceso: dict[str, list[dict]] = {}
        for t in tareas:
            if t.get("estado") == "En Proceso" and t.get("responsable"):
                en_proceso.setdefault(t["responsable"], []).append(t)
        for persona, ts in en_proceso.items():
            if len(ts) > UMBRAL_MULTITASKING:
                detecciones.append({
                    "waste_type": "multitasking", "auto": True,
                    "detalle": f"{persona} tiene {len(ts)} tareas En Proceso "
                               f"(umbral: {UMBRAL_MULTITASKING})."})

        # trabajo_parcial: pausadas viejas sin bloqueo activo reportado
        con_bloqueo_activo = {w["task_id"] for w in waste_events if not w.get("resolved_at")}
        ultima = self._ultima_transicion(transiciones)
        for t in tareas:
            if t.get("estado") != "Pausado" or t["id"] in con_bloqueo_activo:
                continue
            dias = _dias(ultima.get(t["id"]), ahora)
            if dias is not None and dias > UMBRAL_PAUSA_DIAS:
                detecciones.append({
                    "waste_type": "trabajo_parcial", "auto": True,
                    "detalle": f"«{t.get('descripcion', '')[:50]}» lleva {dias:.0f} días "
                               "pausada sin bloqueo reportado."})

        # retrabajo: reaperturas
        for tr in transiciones:
            if tr.get("from_state") == "Completado":
                detecciones.append({
                    "waste_type": "retrabajo", "auto": True,
                    "detalle": f"Tarea {tr['task_id']} reabierta "
                               f"(Completado → {tr['to_state']})."})

        pareto: dict[str, int] = {}
        for w in waste_events:
            pareto[w["waste_type"]] = pareto.get(w["waste_type"], 0) + 1
        for d in detecciones:
            pareto[d["waste_type"]] = pareto.get(d["waste_type"], 0) + 1

        return {
            "pareto": sorted(({"waste_type": k, "eventos": v} for k, v in pareto.items()),
                             key=lambda x: -x["eventos"]),
            "detecciones": detecciones,
            "bloqueos_activos": [w for w in waste_events if not w.get("resolved_at")],
        }

    def little(self, tareas: list[dict], ahora: datetime,
               ventana_dias: int = 28) -> dict:
        """Ley de Little: lead time esperado = WIP / throughput. Si el lead time
        medido es mucho menor, hay tareas zombi infladas en el WIP."""
        wip = sum(1 for t in tareas if t.get("estado") in ESTADOS_WIP)
        completadas = 0
        for t in tareas:
            fc = t.get("fecha_completado")
            if fc and isinstance(fc, str):
                fc = datetime.fromisoformat(fc.replace("Z", "+00:00")).replace(tzinfo=None)
            if fc and (ahora - fc).days <= ventana_dias:
                completadas += 1
        throughput_semanal = round(completadas / (ventana_dias / 7), 2)
        lead_esperado = (round(wip / throughput_semanal * 7, 1)
                         if throughput_semanal else None)
        return {"wip_actual": wip, "throughput_semanal": throughput_semanal,
                "lead_time_esperado_dias": lead_esperado}

    def resumen(self, tareas: list[dict], transiciones: list[dict],
                waste_events: list[dict], ahora: datetime,
                flow_efficiency_avg: Optional[float] = None) -> dict:
        desperdicio = self.detectar_desperdicio(tareas, waste_events, transiciones, ahora)
        return {
            "flow_efficiency_avg": flow_efficiency_avg,
            "tasa_retrabajo": self.tasa_retrabajo(transiciones),
            "little": self.little(tareas, ahora),
            "tareas_zombi": self.tareas_zombi(tareas, transiciones, ahora),
            **desperdicio,
        }
