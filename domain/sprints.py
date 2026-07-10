"""Sprints ligeros estilo Linear Cycles — compromiso, velocity, burndown y carryover.

Puro: opera sobre dicts (sprint, sprint_tasks, tareas) y fechas, sin base de datos.
El burndown se deriva de `fecha_completado` — la memoria histórica de Cenit —
en lugar de snapshots diarios: menos infraestructura, el mismo diagnóstico.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

FIBONACCI = (1, 2, 3, 5, 8, 13, 21)
SOBRE_COMPROMISO = 1.2  # 20% sobre la velocity promedio dispara el aviso


def _a_fecha(valor) -> Optional[date]:
    """Normaliza datetime/date/ISO-string a date."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return datetime.fromisoformat(str(valor).replace("Z", "+00:00")).date()


def _dias_habiles(inicio: date, fin: date) -> list[date]:
    dias, d = [], inicio
    while d <= fin:
        if d.weekday() < 5:  # lunes-viernes
            dias.append(d)
        d += timedelta(days=1)
    return dias


class SprintService:
    """Compromiso, velocity (Say/Do, churn, carryover) y burndown real vs ideal."""

    # ── Planning ─────────────────────────────────────────────────────────

    def validar_compromiso(self, tareas: list[dict],
                           velocity_promedio: Optional[float] = None) -> dict:
        """Valida el compromiso de planning: sin puntos no hay compromiso,
        y comprometer >20% sobre la velocity histórica genera aviso."""
        sin_puntos = [t["id"] for t in tareas if not t.get("story_points")]
        puntos = sum(t.get("story_points") or 0 for t in tareas)
        warning = None
        if sin_puntos:
            warning = (f"{len(sin_puntos)} tarea(s) sin story points — "
                       "estímalas antes de comprometer.")
        elif velocity_promedio and puntos > velocity_promedio * SOBRE_COMPROMISO:
            warning = (f"Sobre-compromiso: {puntos} pts contra una velocity "
                       f"promedio de {velocity_promedio:.0f}.")
        return {"ok": not sin_puntos, "puntos": puntos,
                "sin_puntos": sin_puntos, "warning": warning}

    # ── Velocity / Say-Do ────────────────────────────────────────────────

    def reporte_velocity(self, sprint_tasks: list[dict]) -> dict:
        """Sobre la tabla puente: comprometido vs completado, churn y carryover.
        El Say/Do se calcula contra points_snapshot (la estimación congelada
        al comprometer), no contra el valor vivo de la tarea."""
        activos = [s for s in sprint_tasks if not s.get("removed_at")]
        comprometidos = sum(s.get("points_snapshot") or 0
                            for s in activos if s.get("committed"))
        churn_pts = sum(s.get("points_snapshot") or 0
                        for s in activos if not s.get("committed"))
        completados = sum(s.get("points_snapshot") or 0
                          for s in activos if s.get("completed_in_sprint"))
        completados_comprometidos = sum(
            s.get("points_snapshot") or 0 for s in activos
            if s.get("completed_in_sprint") and s.get("committed"))

        def _pct(num: float) -> Optional[float]:
            return round(num / comprometidos * 100, 1) if comprometidos else None

        return {
            "puntos_comprometidos": comprometidos,
            "puntos_completados": completados,  # velocity real (incluye churn completado)
            "say_do_ratio": _pct(completados_comprometidos),
            "churn_pct": _pct(churn_pts),
            "carryover_pct": _pct(comprometidos - completados_comprometidos),
        }

    def velocity_historico(self, reportes: list[dict]) -> dict:
        """Predictibilidad del equipo sobre los sprints cerrados (orden cronológico)."""
        vels = [r["puntos_completados"] for r in reportes]
        says = [r["say_do_ratio"] for r in reportes if r.get("say_do_ratio") is not None]
        ult3 = vels[-3:]
        return {
            "sprints": len(reportes),
            "velocity_promedio": round(sum(vels) / len(vels), 1) if vels else None,
            "velocity_promedio_3": round(sum(ult3) / len(ult3), 1) if ult3 else None,
            "say_do_promedio": round(sum(says) / len(says), 1) if says else None,
        }

    # ── Burndown ─────────────────────────────────────────────────────────

    def burndown(self, sprint: dict, sprint_tasks: list[dict],
                 tareas_por_id: dict[int, dict], hoy: date) -> dict:
        """Serie real vs ideal por día hábil. Real = total − puntos de tareas
        con fecha_completado ≤ día. Ideal = recta de total a 0."""
        activos = [s for s in sprint_tasks if not s.get("removed_at")]
        total = sum(s.get("points_snapshot") or 0 for s in activos)
        inicio, fin = _a_fecha(sprint["fecha_inicio"]), _a_fecha(sprint["fecha_fin"])
        dias = _dias_habiles(inicio, fin)
        if not dias or total == 0:
            return {"puntos_totales": total, "serie": [],
                    "desviacion_actual": None, "alerta": None}

        completado_en: dict[int, date] = {}
        for s in activos:
            fc = _a_fecha(tareas_por_id.get(s["task_id"], {}).get("fecha_completado"))
            if fc:
                completado_en[s["task_id"]] = fc

        D = max(len(dias) - 1, 1)
        serie = []
        for i, dia in enumerate(dias):
            if dia > hoy:
                break
            quemado = sum(s.get("points_snapshot") or 0 for s in activos
                          if completado_en.get(s["task_id"]) and completado_en[s["task_id"]] <= dia)
            serie.append({
                "fecha": dia,
                "restante_real": round(total - quemado, 1),
                "restante_ideal": round(total * (1 - i / D), 1),
            })

        desviacion = alerta = None
        if serie:
            desviacion = round(serie[-1]["restante_real"] - serie[-1]["restante_ideal"], 1)
            alerta = "atraso" if desviacion > 0 else ("adelanto" if desviacion < 0 else "en_linea")
        return {"puntos_totales": total, "serie": serie,
                "desviacion_actual": desviacion, "alerta": alerta}

    # ── Cierre ───────────────────────────────────────────────────────────

    def cerrar(self, sprint: dict, sprint_tasks: list[dict],
               tareas_por_id: dict[int, dict]) -> dict:
        """Marca qué se completó dentro del sprint y propone el carryover.
        No mueve nada automáticamente: la lista es para que el líder decida."""
        fin = _a_fecha(sprint["fecha_fin"])
        completadas, carryover = [], []
        for s in sprint_tasks:
            if s.get("removed_at"):
                continue
            t = tareas_por_id.get(s["task_id"], {})
            fc = _a_fecha(t.get("fecha_completado"))
            done = t.get("estado") == "Completado" and (fc is None or fc <= fin)
            s["completed_in_sprint"] = done
            if done:
                completadas.append(s["task_id"])
            else:
                carryover.append({
                    "task_id": s["task_id"],
                    "story_points": s.get("points_snapshot"),
                    "descripcion": t.get("descripcion"),
                })
        return {
            "completadas": completadas,
            "carryover_sugerido": carryover,
            **self.reporte_velocity(sprint_tasks),
        }
