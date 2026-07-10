"""Reporte semanal ejecutivo — estado, riesgos y próximos bloqueos.

Puro: recibe los resúmenes ya calculados por los motores (flow, lean, riesgo)
y devuelve un dict estructurado + su render en markdown. El cron de Vercel
solo dispara; la inteligencia vive aquí, testeable sin DB ni scheduler.
"""

from __future__ import annotations

from datetime import date
from typing import Optional


class ReportService:
    """Ensambla el pulso semanal que un líder leería en 2 minutos un lunes."""

    def generar(self, *, semana_inicio: date, semana_fin: date,
                summary: dict, flow: dict, lean: dict,
                riesgos: list[dict], completadas_semana: list[dict],
                vencen_pronto: list[dict]) -> dict:
        pulso = {
            "abiertas": summary.get("total", 0) - summary.get("completadas", 0),
            "completadas_semana": len(completadas_semana),
            "lead_time_avg": flow.get("lead_time_avg"),
            "flow_efficiency_avg": flow.get("flow_efficiency_avg"),
            "wip": lean.get("little", {}).get("wip_actual"),
            "tasa_retrabajo": lean.get("tasa_retrabajo"),
        }
        criticos = [r for r in riesgos if r.get("nivel_riesgo") in ("crítico", "alto")][:5]
        return {
            "semana_inicio": semana_inicio,
            "semana_fin": semana_fin,
            "pulso": pulso,
            "riesgos": [{"id": r["id"], "descripcion": r.get("descripcion"),
                         "nivel": r["nivel_riesgo"], "score": r["score_normalizado"],
                         "responsable": r.get("responsable")} for r in criticos],
            "bloqueos_activos": lean.get("bloqueos_activos", []),
            "tareas_zombi": lean.get("tareas_zombi", [])[:5],
            "detecciones": lean.get("detecciones", [])[:5],
            "vencen_pronto": [{"id": t["id"], "descripcion": t.get("descripcion"),
                               "fecha_fin": t.get("fecha_fin"),
                               "responsable": t.get("responsable")}
                              for t in vencen_pronto[:8]],
            "recomendaciones": self._recomendaciones(pulso, lean, criticos),
        }

    def _recomendaciones(self, pulso: dict, lean: dict, criticos: list[dict]) -> list[str]:
        """Reglas explícitas, sin IA (esa llega en V3 con historial suficiente)."""
        recs: list[str] = []
        little = lean.get("little", {})
        esperado = little.get("lead_time_esperado_dias")
        medido = pulso.get("lead_time_avg")
        if esperado and medido and esperado > medido * 2:
            recs.append(
                f"La Ley de Little proyecta {esperado:.0f} días de lead time con el WIP "
                f"actual ({little.get('wip_actual')}), pero el medido es {medido:.0f}: hay "
                "inventario zombi inflando el tablero — cierra o cancela lo que no avanza.")
        if lean.get("tareas_zombi"):
            z = lean["tareas_zombi"][0]
            recs.append(
                f"{len(lean['tareas_zombi'])} tarea(s) sin moverse hace >14 días; la más "
                f"vieja lleva {z['dias_sin_movimiento']:.0f} días («{(z.get('descripcion') or '')[:40]}»).")
        multitask = [d for d in lean.get("detecciones", []) if d["waste_type"] == "multitasking"]
        if multitask:
            recs.append(multitask[0]["detalle"] + " Repartir o pausar reduce el lead time de todos.")
        if criticos:
            recs.append(f"{len(criticos)} tarea(s) en riesgo crítico/alto — revisarlas "
                        "hoy antes de que escalen.")
        if pulso.get("completadas_semana") == 0:
            recs.append("Cero tareas completadas esta semana: ¿compromiso demasiado grande "
                        "o bloqueos sin reportar?")
        return recs

    # ── Render ───────────────────────────────────────────────────────────

    def a_markdown(self, r: dict) -> str:
        p = r["pulso"]

        def _v(x, suf="") -> str:
            return f"{x}{suf}" if x is not None else "—"

        lineas = [
            f"# 🏔️ Cenit — Reporte semanal ({r['semana_inicio']} → {r['semana_fin']})",
            "",
            "## Pulso",
            f"- Tareas abiertas: **{_v(p['abiertas'])}** · WIP: **{_v(p['wip'])}**",
            f"- Completadas esta semana: **{_v(p['completadas_semana'])}**",
            f"- Lead time promedio: **{_v(p['lead_time_avg'], ' d')}** · "
            f"Flow efficiency: **{_v(p['flow_efficiency_avg'], '%')}**",
            f"- Tasa de retrabajo: **{_v(p['tasa_retrabajo'], '%')}**",
        ]
        if r["riesgos"]:
            lineas += ["", "## ⚠️ Riesgos que atender"]
            lineas += [f"- **{x['nivel']}** ({x['score']}) — {x['descripcion']} · "
                       f"{x['responsable'] or 'Sin asignar'}" for x in r["riesgos"]]
        if r["bloqueos_activos"] or r["tareas_zombi"]:
            lineas += ["", "## 🚧 Bloqueos y estancamiento"]
            lineas += [f"- Bloqueo `{b['waste_type']}`: {b.get('descripcion') or 'sin detalle'} "
                       f"(tarea {b['task_id']})" for b in r["bloqueos_activos"]]
            lineas += [f"- Zombi: {z.get('descripcion')} — {z['dias_sin_movimiento']:.0f} días "
                       f"sin moverse" for z in r["tareas_zombi"]]
        if r["vencen_pronto"]:
            lineas += ["", "## 📅 Vencen esta semana"]
            lineas += [f"- {t['descripcion']} · {t['responsable'] or 'Sin asignar'} "
                       f"(vence {str(t['fecha_fin'])[:10]})" for t in r["vencen_pronto"]]
        if r["recomendaciones"]:
            lineas += ["", "## 💡 Recomendaciones"]
            lineas += [f"- {rec}" for rec in r["recomendaciones"]]
        return "\n".join(lineas)
