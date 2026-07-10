"""Tests del SprintService — sprints ligeros puros, sin base de datos."""

from datetime import date

from domain.sprints import SprintService

SVC = SprintService()


def _st(task_id, points, committed=True, removed=False, done=False):
    return {"task_id": task_id, "points_snapshot": points, "committed": committed,
            "removed_at": "2026-07-01" if removed else None, "completed_in_sprint": done}


def _tarea(tid, estado="En Proceso", fecha_completado=None, points=3):
    return {"id": tid, "estado": estado, "descripcion": f"Tarea {tid}",
            "fecha_completado": fecha_completado, "story_points": points}


class TestCompromiso:
    def test_rechaza_tareas_sin_puntos(self):
        v = SVC.validar_compromiso([_tarea(1, points=None), _tarea(2, points=3)])
        assert v["ok"] is False
        assert v["sin_puntos"] == [1]

    def test_suma_puntos(self):
        v = SVC.validar_compromiso([_tarea(1, points=3), _tarea(2, points=5)])
        assert v["ok"] is True
        assert v["puntos"] == 8
        assert v["warning"] is None

    def test_avisa_sobre_compromiso(self):
        # 13 pts contra velocity de 10 → excede el margen del 20%
        v = SVC.validar_compromiso([_tarea(1, points=13)], velocity_promedio=10)
        assert v["ok"] is True  # avisa, no bloquea — misma filosofía que el WIP
        assert "Sobre-compromiso" in v["warning"]


class TestVelocity:
    def test_say_do_churn_carryover(self):
        sts = [
            _st(1, 5, committed=True, done=True),
            _st(2, 3, committed=True, done=False),   # carryover
            _st(3, 2, committed=False, done=True),   # churn completado
            _st(4, 8, committed=True, removed=True), # descoped: no cuenta
        ]
        r = SVC.reporte_velocity(sts)
        assert r["puntos_comprometidos"] == 8      # 5 + 3 (el descoped no cuenta)
        assert r["puntos_completados"] == 7        # 5 + 2 (churn completado suma velocity)
        assert r["say_do_ratio"] == 62.5           # 5 / 8
        assert r["churn_pct"] == 25.0              # 2 / 8
        assert r["carryover_pct"] == 37.5          # 3 / 8

    def test_sin_comprometidos_no_divide_por_cero(self):
        r = SVC.reporte_velocity([_st(1, 2, committed=False)])
        assert r["say_do_ratio"] is None

    def test_historico(self):
        reportes = [{"puntos_completados": 10, "say_do_ratio": 80.0},
                    {"puntos_completados": 14, "say_do_ratio": 90.0}]
        h = SVC.velocity_historico(reportes)
        assert h["velocity_promedio"] == 12.0
        assert h["say_do_promedio"] == 85.0


class TestBurndown:
    SPRINT = {"fecha_inicio": date(2026, 7, 6), "fecha_fin": date(2026, 7, 10)}  # lun-vie

    def test_ideal_baja_linealmente_y_real_refleja_completadas(self):
        sts = [_st(1, 4), _st(2, 4)]
        tareas = {1: _tarea(1, "Completado", fecha_completado=date(2026, 7, 8)),
                  2: _tarea(2)}
        b = SVC.burndown(self.SPRINT, sts, tareas, hoy=date(2026, 7, 10))
        assert b["puntos_totales"] == 8
        assert len(b["serie"]) == 5  # 5 días hábiles
        assert b["serie"][0]["restante_ideal"] == 8.0
        assert b["serie"][-1]["restante_ideal"] == 0.0
        # La tarea 1 (4 pts) se completó el mié 8 → el real cae ese día
        assert b["serie"][1]["restante_real"] == 8.0   # martes
        assert b["serie"][2]["restante_real"] == 4.0   # miércoles
        assert b["desviacion_actual"] == 4.0           # 4 real − 0 ideal
        assert b["alerta"] == "atraso"

    def test_serie_se_corta_en_hoy(self):
        sts = [_st(1, 5)]
        b = SVC.burndown(self.SPRINT, sts, {1: _tarea(1)}, hoy=date(2026, 7, 7))
        assert len(b["serie"]) == 2  # lunes y martes

    def test_sin_puntos_no_hay_serie(self):
        b = SVC.burndown(self.SPRINT, [], {}, hoy=date(2026, 7, 10))
        assert b["serie"] == []
        assert b["alerta"] is None


class TestCierre:
    SPRINT = {"fecha_inicio": date(2026, 7, 6), "fecha_fin": date(2026, 7, 10)}

    def test_separa_completadas_de_carryover(self):
        sts = [_st(1, 5), _st(2, 3)]
        tareas = {1: _tarea(1, "Completado", fecha_completado=date(2026, 7, 9)),
                  2: _tarea(2, "En Proceso")}
        r = SVC.cerrar(dict(self.SPRINT), sts, tareas)
        assert r["completadas"] == [1]
        assert [c["task_id"] for c in r["carryover_sugerido"]] == [2]
        assert r["say_do_ratio"] == 62.5

    def test_completada_despues_del_fin_no_cuenta(self):
        sts = [_st(1, 5)]
        tareas = {1: _tarea(1, "Completado", fecha_completado=date(2026, 7, 15))}
        r = SVC.cerrar(dict(self.SPRINT), sts, tareas)
        assert r["completadas"] == []
        assert len(r["carryover_sugerido"]) == 1
