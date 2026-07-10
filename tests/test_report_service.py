"""Tests del ReportService — reporte semanal puro, sin DB ni scheduler."""

from datetime import date

from domain.reports import ReportService

SVC = ReportService()

BASE = dict(
    semana_inicio=date(2026, 7, 6), semana_fin=date(2026, 7, 12),
    summary={"total": 30, "completadas": 10},
    flow={"lead_time_avg": 8.0, "flow_efficiency_avg": 75.0},
    lean={"little": {"wip_actual": 12, "lead_time_esperado_dias": 40.0},
          "tasa_retrabajo": 5.0, "tareas_zombi": [], "detecciones": [],
          "bloqueos_activos": []},
    riesgos=[], completadas_semana=[], vencen_pronto=[],
)


def _gen(**overrides):
    return SVC.generar(**{**BASE, **overrides})


class TestGenerar:
    def test_estructura(self):
        r = _gen()
        for clave in ("pulso", "riesgos", "bloqueos_activos", "tareas_zombi",
                      "vencen_pronto", "recomendaciones"):
            assert clave in r
        assert r["pulso"]["abiertas"] == 20
        assert r["pulso"]["wip"] == 12

    def test_riesgos_solo_criticos_y_altos(self):
        riesgos = [
            {"id": 1, "descripcion": "A", "nivel_riesgo": "crítico",
             "score_normalizado": 20, "responsable": "Ana"},
            {"id": 2, "descripcion": "B", "nivel_riesgo": "medio",
             "score_normalizado": 5, "responsable": None},
        ]
        r = _gen(riesgos=riesgos)
        assert [x["id"] for x in r["riesgos"]] == [1]


class TestRecomendaciones:
    def test_little_muy_sobre_medido_delata_zombis(self):
        # esperado 40 vs medido 8 → >2x → recomendación de inventario zombi
        r = _gen()
        assert any("Little" in rec for rec in r["recomendaciones"])

    def test_semana_sin_completadas(self):
        r = _gen()
        assert any("Cero tareas completadas" in rec for rec in r["recomendaciones"])

    def test_multitasking_llega_al_reporte(self):
        lean = {**BASE["lean"],
                "detecciones": [{"waste_type": "multitasking",
                                 "detalle": "Ana tiene 5 tareas En Proceso (umbral: 3)."}]}
        r = _gen(lean=lean)
        assert any("Ana tiene 5" in rec for rec in r["recomendaciones"])

    def test_flujo_sano_sin_recomendaciones_falsas(self):
        lean = {"little": {"wip_actual": 5, "lead_time_esperado_dias": 9.0},
                "tasa_retrabajo": 0.0, "tareas_zombi": [], "detecciones": [],
                "bloqueos_activos": []}
        r = _gen(lean=lean, flow={"lead_time_avg": 8.0, "flow_efficiency_avg": 90.0},
                 completadas_semana=[{"id": 1}])
        assert r["recomendaciones"] == []


class TestMarkdown:
    def test_render_contiene_secciones(self):
        r = _gen(
            riesgos=[{"id": 1, "descripcion": "Migrar S3", "nivel_riesgo": "crítico",
                      "score_normalizado": 20, "responsable": "Fidel"}],
            vencen_pronto=[{"id": 2, "descripcion": "Piloto UniAndes",
                            "fecha_fin": "2026-07-10T00:00:00", "responsable": None}],
        )
        md = SVC.a_markdown(r)
        assert "# 🏔️ Cenit — Reporte semanal" in md
        assert "## Pulso" in md
        assert "## ⚠️ Riesgos que atender" in md
        assert "Migrar S3" in md
        assert "## 📅 Vencen esta semana" in md
        assert "vence 2026-07-10" in md

    def test_valores_nulos_se_renderizan_como_guion(self):
        r = _gen(flow={"lead_time_avg": None, "flow_efficiency_avg": None})
        md = SVC.a_markdown(r)
        assert "Lead time promedio: **—**" in md
