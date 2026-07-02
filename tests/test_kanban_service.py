from domain.services import KanbanService
from tests.conftest import make_raw


class TestKanbanService:
    svc = KanbanService()

    def test_agrupar_por_estado_crea_4_columnas(self):
        cols = self.svc.agrupar_por_estado([])
        assert len(cols) == 4

    def test_asigna_tareas_a_la_columna_correcta(self):
        tareas = [
            make_raw(id=1, estado="En Proceso"),
            make_raw(id=2, estado="En Proceso"),
            make_raw(id=3, estado="Completado"),
        ]
        cols = self.svc.agrupar_por_estado(tareas)
        assert len(cols["En Proceso"]) == 2
        assert len(cols["Completado"]) == 1
        assert len(cols["No Iniciado"]) == 0

    def test_mover_tarea_cambia_de_columna(self):
        tareas = [make_raw(id=1, estado="No Iniciado")]
        before = self.svc.agrupar_por_estado(tareas)
        assert len(before["No Iniciado"]) == 1

        tareas[0]["estado"] = "En Proceso"
        after = self.svc.agrupar_por_estado(tareas)
        assert len(after["No Iniciado"]) == 0
        assert len(after["En Proceso"]) == 1

    def test_estado_desconocido_cae_en_no_iniciado(self):
        tareas = [make_raw(id=1, estado="Inventado")]
        cols = self.svc.agrupar_por_estado(tareas)
        assert len(cols["No Iniciado"]) == 1
