"""Servicios de negocio de Cenit (portados de src/services/*.ts).

Operan sobre dicts tal como los devuelve la API (TaskOut serializado),
igual que los servicios TypeScript operaban sobre TareaRaw.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

ESTADOS: list[str] = ["No Iniciado", "En Proceso", "Pausado", "Completado"]

ESTADO_COLORS: dict[str, str] = {
    "No Iniciado": "#64748B",
    "En Proceso": "#3B82F6",
    "Pausado": "#F59E0B",
    "Completado": "#10B981",
}

PRIO_COLORS: dict[str, str] = {
    "Urgente": "#EF4444",
    "Alta": "#F59E0B",
    "Media": "#14B8A6",
    "Baja": "#64748B",
}

EIS_LABELS: dict[str, str] = {
    "Q1": "🔴 Q1 — Hacer ya",
    "Q2": "🔵 Q2 — Planificar",
    "Q3": "🟡 Q3 — Delegar",
    "Q4": "⚫ Q4 — Posponer",
}

_PROYECTOS_IMPORTANTES = {"Desarrollo", "Operaciones", "Generador", "Wallet"}


class KanbanService:
    def agrupar_por_estado(self, tareas: list[dict]) -> dict[str, list[dict]]:
        cols: dict[str, list[dict]] = {e: [] for e in ESTADOS}
        for t in tareas:
            col = t.get("estado") if t.get("estado") in cols else "No Iniciado"
            cols[col].append(t)
        return cols

    def color_estado(self, estado: str) -> str:
        return ESTADO_COLORS.get(estado, "#64748B")


class EisenhowerService:
    @staticmethod
    def clasificar(tarea: dict) -> str:
        if tarea.get("eisenhower"):
            return tarea["eisenhower"]

        es_urgente = tarea.get("prioridad") == "Urgente"
        es_importante = (tarea.get("proyecto") or "") in _PROYECTOS_IMPORTANTES

        if es_urgente and es_importante:
            return "Q1"
        if not es_urgente and es_importante:
            return "Q2"
        if es_urgente and not es_importante:
            return "Q3"
        return "Q4"

    def agrupar_en_cuadrantes(self, tareas: list[dict]) -> dict[str, list[dict]]:
        quads: dict[str, list[dict]] = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}
        for t in tareas:
            if t.get("estado") == "Completado":
                continue
            quads[EisenhowerService.clasificar(t)].append(t)
        return quads


class RiesgoService:
    @staticmethod
    def nivel_desde_score(score: float) -> str:
        if score >= 15:
            return "crítico"
        if score >= 8:
            return "alto"
        if score >= 4:
            return "medio"
        return "bajo"

    def ordenar_por_riesgo(self, tareas: list[dict]) -> list[dict]:
        candidatas = [
            t for t in tareas
            if t.get("estado") != "Completado" and t.get("risk_score") is not None
        ]
        candidatas.sort(key=lambda t: t.get("risk_score") or 0, reverse=True)
        return [
            {
                **t,
                "nivel_riesgo": RiesgoService.nivel_desde_score(t.get("risk_score") or 0),
                "score_normalizado": t.get("risk_score") or 0,
            }
            for t in candidatas[:30]
        ]


class AnalyticsService:
    def por_responsable(self, tareas: list[dict]) -> list[dict]:
        stats: dict[str, dict] = {}
        for t in tareas:
            r = t.get("responsable") or "Sin asignar"
            s = stats.setdefault(
                r, {"nombre": r, "total": 0, "completadas": 0, "lead_times": []}
            )
            s["total"] += 1
            if t.get("estado") == "Completado":
                s["completadas"] += 1
                if t.get("lead_time_days") is not None:
                    s["lead_times"].append(t["lead_time_days"])

        result = []
        for s in stats.values():
            lts = s["lead_times"]
            result.append({**s, "avg_lead_time": sum(lts) / len(lts) if lts else None})
        return sorted(result, key=lambda s: -s["total"])

    def por_prioridad(self, tareas: list[dict]) -> dict[str, int]:
        acc: dict[str, int] = {}
        for t in tareas:
            p = t.get("prioridad")
            acc[p] = acc.get(p, 0) + 1
        return acc

    def throughput_mensual(self, tareas: list[dict]) -> list[dict]:
        monthly: dict[str, int] = {}
        for t in tareas:
            fc = t.get("fecha_completado")
            if fc:
                mes = str(fc)[:7]
                monthly[mes] = monthly.get(mes, 0) + 1
        return [
            {"mes": mes, "count": count}
            for mes, count in sorted(monthly.items())[-6:]
        ]


class FlowService:
    """Métricas de flujo derivadas del historial de transiciones de estado.

    Opera sobre una lista de dicts {task_id, from_state, to_state, changed_at:datetime},
    sin depender de la base de datos — testeable en aislamiento.
    """

    def metricas_por_tarea(self, transiciones: list[dict], ahora: datetime) -> dict[int, dict]:
        grupos: dict[int, list[dict]] = {}
        for t in transiciones:
            grupos.setdefault(t["task_id"], []).append(t)

        resultado: dict[int, dict] = {}
        for task_id, trs in grupos.items():
            trs = sorted(trs, key=lambda x: x["changed_at"])
            creado = trs[0]["changed_at"]
            entrada_proceso = next((x["changed_at"] for x in trs if x["to_state"] == "En Proceso"), None)
            completado = None
            for x in trs:
                if x["to_state"] == "Completado":
                    completado = x["changed_at"]

            # Tiempo acumulado en cada estado (el último se extiende hasta 'ahora')
            tiempo_estado: dict[str, float] = {}
            for i, x in enumerate(trs):
                fin = trs[i + 1]["changed_at"] if i + 1 < len(trs) else ahora
                dur = max((fin - x["changed_at"]).total_seconds(), 0)
                tiempo_estado[x["to_state"]] = tiempo_estado.get(x["to_state"], 0) + dur

            activo = tiempo_estado.get("En Proceso", 0)
            pausa = tiempo_estado.get("Pausado", 0)
            flow_eff = round(activo / (activo + pausa) * 100, 1) if (activo + pausa) > 0 else None

            estado_actual = trs[-1]["to_state"]
            abierta = estado_actual != "Completado"

            resultado[task_id] = {
                "estado_actual": estado_actual,
                "lead_time_days": round((completado - creado).total_seconds() / 86400, 1) if completado else None,
                "cycle_time_days": round((completado - entrada_proceso).total_seconds() / 86400, 1) if (completado and entrada_proceso) else None,
                "flow_efficiency": flow_eff,
                "aging_days": round((ahora - trs[-1]["changed_at"]).total_seconds() / 86400, 1) if abierta else None,
            }
        return resultado

    def resumen(self, transiciones: list[dict], ahora: datetime) -> dict:
        por_tarea = self.metricas_por_tarea(transiciones, ahora)

        def _prom(campo: str) -> Optional[float]:
            xs = [m[campo] for m in por_tarea.values() if m[campo] is not None]
            return round(sum(xs) / len(xs), 1) if xs else None

        return {
            "tareas": len(por_tarea),
            "lead_time_avg": _prom("lead_time_days"),
            "cycle_time_avg": _prom("cycle_time_days"),
            "flow_efficiency_avg": _prom("flow_efficiency"),
            "aging_avg": _prom("aging_days"),
            "por_tarea": por_tarea,
        }


class WipService:
    """Límites WIP explícitos — la práctica central de Kanban que casi nadie implementa.

    Opera sobre dicts de tareas y de configuración de columnas
    ({estado, wip_limit, wip_limit_scope}), sin tocar la base de datos.
    Cenit persuade, no bloquea: el veredicto alimenta avisos, nunca un candado.
    """

    def ocupacion(self, tareas: list[dict], columnas: list[dict]) -> dict[str, dict]:
        """Ocupación de cada columna contra su límite: ok | al_limite | excedido | sin_limite."""
        resultado: dict[str, dict] = {}
        for col in columnas:
            estado = col["estado"]
            en_col = [t for t in tareas if t.get("estado") == estado]
            por_persona: dict[str, int] = {}
            for t in en_col:
                p = t.get("responsable") or "Sin asignar"
                por_persona[p] = por_persona.get(p, 0) + 1

            limite = col.get("wip_limit")
            scope = col.get("wip_limit_scope") or "board"
            if limite is None:
                status = "sin_limite"
            else:
                # Con scope 'person' manda la persona más cargada, no el total
                medido = max(por_persona.values(), default=0) if scope == "person" else len(en_col)
                status = "excedido" if medido > limite else ("al_limite" if medido == limite else "ok")

            resultado[estado] = {
                "ocupacion": len(en_col),
                "wip_limit": limite,
                "scope": scope,
                "status": status,
                "por_persona": por_persona,
            }
        return resultado

    def evaluar_movimiento(
        self, tareas: list[dict], columnas: list[dict],
        estado_destino: str, responsable: Optional[str] = None,
    ) -> dict:
        """¿Meter una tarea más en `estado_destino` rompe su límite?

        Devuelve el veredicto más el contexto del aviso: ocupación actual,
        límite y las tareas más antiguas de la columna (terminar antes de empezar).
        """
        col = next((c for c in columnas if c["estado"] == estado_destino), None)
        limite = col.get("wip_limit") if col else None
        if limite is None:
            return {"excedido": False, "wip_limit": None, "wip_actual": None,
                    "scope": "board", "tareas_mas_antiguas": []}

        en_col = [t for t in tareas if t.get("estado") == estado_destino]
        scope = col.get("wip_limit_scope") or "board"
        if scope == "person":
            p = responsable or "Sin asignar"
            actual = sum(1 for t in en_col if (t.get("responsable") or "Sin asignar") == p)
        else:
            actual = len(en_col)

        excedido = actual + 1 > limite
        mas_antiguas = sorted(
            en_col, key=lambda t: str(t.get("fecha_inicio") or t.get("created_at") or ""),
        )[:3] if excedido else []
        return {
            "excedido": excedido,
            "wip_limit": limite,
            "wip_actual": actual,
            "scope": scope,
            "tareas_mas_antiguas": [
                {"id": t.get("id"), "descripcion": t.get("descripcion"),
                 "responsable": t.get("responsable")}
                for t in mas_antiguas
            ],
        }


class FiltroService:
    def filtrar(
        self,
        tareas: list[dict],
        entidad: str = "",
        prioridad: str = "",
        responsable: str = "",
        search: str = "",
    ) -> list[dict]:
        q = search.lower().strip()
        result = []
        for t in tareas:
            if entidad and t.get("entidad") != entidad:
                continue
            if prioridad and t.get("prioridad") != prioridad:
                continue
            if responsable and t.get("responsable") != responsable:
                continue
            if q:
                desc = (t.get("descripcion") or "").lower()
                cli = (t.get("cliente") or "").lower()
                if q not in desc and q not in cli:
                    continue
            result.append(t)
        return result

    def filtrar_por_entidad(self, tareas: list[dict], entidad: str) -> list[dict]:
        if not entidad:
            return tareas
        return [t for t in tareas if t.get("entidad") == entidad]
