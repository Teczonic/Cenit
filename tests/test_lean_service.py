"""Tests del LeanService — desperdicio, retrabajo, zombis y Little, sin DB."""

from datetime import datetime, timedelta

from domain.lean import LeanService

SVC = LeanService()
AHORA = datetime(2026, 7, 9, 12, 0)


def _t(tid, estado="En Proceso", responsable=None, fecha_completado=None, descripcion=None):
    return {"id": tid, "estado": estado, "responsable": responsable,
            "descripcion": descripcion or f"Tarea {tid}",
            "fecha_completado": fecha_completado}


def _tr(task_id, to_state, dias_atras, from_state=None):
    return {"task_id": task_id, "from_state": from_state, "to_state": to_state,
            "changed_at": AHORA - timedelta(days=dias_atras)}


class TestRetrabajo:
    def test_sin_completadas_es_cero(self):
        assert SVC.tasa_retrabajo([_tr(1, "En Proceso", 3)]) == 0.0

    def test_reaperturas_sobre_completadas(self):
        trs = [
            _tr(1, "Completado", 10),
            _tr(2, "Completado", 8),
            _tr(1, "En Proceso", 5, from_state="Completado"),  # reabierta
        ]
        assert SVC.tasa_retrabajo(trs) == 50.0


class TestZombis:
    def test_wip_viejo_es_zombi(self):
        tareas = [_t(1, "En Proceso"), _t(2, "Pausado"), _t(3, "Completado")]
        trs = [_tr(1, "En Proceso", 20), _tr(2, "Pausado", 3), _tr(3, "Completado", 30)]
        zombis = SVC.tareas_zombi(tareas, trs, AHORA)
        assert [z["id"] for z in zombis] == [1]  # la 2 es reciente, la 3 no es WIP
        assert zombis[0]["dias_sin_movimiento"] == 20.0


class TestDesperdicio:
    def test_detecta_multitasking(self):
        tareas = [_t(i, "En Proceso", responsable="Ana") for i in range(4)]
        res = SVC.detectar_desperdicio(tareas, [], [], AHORA)
        tipos = [d["waste_type"] for d in res["detecciones"]]
        assert "multitasking" in tipos

    def test_detecta_trabajo_parcial_en_pausas_viejas(self):
        tareas = [_t(1, "Pausado")]
        trs = [_tr(1, "Pausado", 10)]
        res = SVC.detectar_desperdicio(tareas, [], trs, AHORA)
        assert any(d["waste_type"] == "trabajo_parcial" for d in res["detecciones"])

    def test_pausa_con_bloqueo_reportado_no_duplica(self):
        tareas = [_t(1, "Pausado")]
        trs = [_tr(1, "Pausado", 10)]
        waste = [{"id": 1, "task_id": 1, "waste_type": "espera", "resolved_at": None}]
        res = SVC.detectar_desperdicio(tareas, waste, trs, AHORA)
        assert not any(d["waste_type"] == "trabajo_parcial" for d in res["detecciones"])
        assert len(res["bloqueos_activos"]) == 1

    def test_detecta_retrabajo_en_reaperturas(self):
        trs = [_tr(1, "En Proceso", 2, from_state="Completado")]
        res = SVC.detectar_desperdicio([], [], trs, AHORA)
        assert any(d["waste_type"] == "retrabajo" for d in res["detecciones"])

    def test_pareto_ordenado_combina_reportado_y_detectado(self):
        tareas = [_t(i, "En Proceso", responsable="Ana") for i in range(4)]
        waste = [
            {"id": 1, "task_id": 9, "waste_type": "espera", "resolved_at": None},
            {"id": 2, "task_id": 8, "waste_type": "espera", "resolved_at": AHORA},
        ]
        res = SVC.detectar_desperdicio(tareas, waste, [], AHORA)
        assert res["pareto"][0]["waste_type"] == "espera"   # 2 eventos
        assert res["pareto"][0]["eventos"] == 2


class TestLittle:
    def test_lead_time_esperado(self):
        # 6 en WIP, 4 completadas en la ventana de 28 días → 1/semana
        tareas = ([_t(i, "En Proceso") for i in range(4)]
                  + [_t(10, "Pausado"), _t(11, "Pausado")]
                  + [_t(20 + i, "Completado",
                        fecha_completado=AHORA - timedelta(days=i * 5)) for i in range(4)])
        r = SVC.little(tareas, AHORA)
        assert r["wip_actual"] == 6
        assert r["throughput_semanal"] == 1.0
        assert r["lead_time_esperado_dias"] == 42.0  # 6 / 1 * 7

    def test_sin_throughput_no_divide_por_cero(self):
        r = SVC.little([_t(1, "En Proceso")], AHORA)
        assert r["lead_time_esperado_dias"] is None


class TestResumen:
    def test_estructura_completa(self):
        r = SVC.resumen([_t(1)], [_tr(1, "En Proceso", 1)], [], AHORA,
                        flow_efficiency_avg=72.5)
        for clave in ("flow_efficiency_avg", "tasa_retrabajo", "little",
                      "tareas_zombi", "pareto", "detecciones", "bloqueos_activos"):
            assert clave in r
        assert r["flow_efficiency_avg"] == 72.5
