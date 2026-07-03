from datetime import datetime, timedelta

from domain.services import FlowService

BASE = datetime(2026, 1, 1)


def _t(task_id, to_state, dia, from_state=None):
    return {"task_id": task_id, "from_state": from_state,
            "to_state": to_state, "changed_at": BASE + timedelta(days=dia)}


class TestFlowService:
    svc = FlowService()

    def test_lead_y_cycle_time_de_tarea_completada(self):
        # No Iniciado(d0) -> En Proceso(d1) -> Pausado(d2) -> En Proceso(d3) -> Completado(d5)
        trans = [
            _t(1, "No Iniciado", 0),
            _t(1, "En Proceso", 1, "No Iniciado"),
            _t(1, "Pausado", 2, "En Proceso"),
            _t(1, "En Proceso", 3, "Pausado"),
            _t(1, "Completado", 5, "En Proceso"),
        ]
        m = self.svc.metricas_por_tarea(trans, BASE + timedelta(days=10))[1]
        assert m["lead_time_days"] == 5.0          # d5 - d0
        assert m["cycle_time_days"] == 4.0         # d5 - primera entrada a En Proceso (d1)
        assert m["aging_days"] is None             # completada
        # activo = (d2-d1) + (d5-d3) = 1 + 2 = 3 días; pausa = (d3-d2) = 1 día
        assert m["flow_efficiency"] == 75.0        # 3 / (3+1) * 100

    def test_aging_de_tarea_abierta(self):
        trans = [
            _t(2, "No Iniciado", 0),
            _t(2, "En Proceso", 1, "No Iniciado"),
        ]
        ahora = BASE + timedelta(days=6)
        m = self.svc.metricas_por_tarea(trans, ahora)[2]
        assert m["lead_time_days"] is None         # no completada
        assert m["cycle_time_days"] is None
        assert m["aging_days"] == 5.0              # ahora(d6) - última transición(d1)
        assert m["estado_actual"] == "En Proceso"

    def test_resumen_promedia_solo_valores_presentes(self):
        trans = [
            _t(1, "No Iniciado", 0), _t(1, "En Proceso", 1), _t(1, "Completado", 3),
            _t(2, "No Iniciado", 0), _t(2, "En Proceso", 1),  # abierta, sin lead time
        ]
        r = self.svc.resumen(trans, BASE + timedelta(days=5))
        assert r["tareas"] == 2
        assert r["lead_time_avg"] == 3.0           # solo la tarea 1 aporta
        assert r["aging_avg"] == 4.0               # solo la tarea 2 aporta (d5 - d1)
