from domain.services import EisenhowerService
from tests.conftest import make_raw


class TestClasificar:
    def test_urgente_mas_desarrollo_es_q1_hacer_ya(self):
        t = make_raw(prioridad="Urgente", proyecto="Desarrollo")
        assert EisenhowerService.clasificar(t) == "Q1"

    def test_alta_mas_operaciones_es_q2_planificar(self):
        t = make_raw(prioridad="Alta", proyecto="Operaciones")
        assert EisenhowerService.clasificar(t) == "Q2"

    def test_urgente_mas_marketing_es_q3_delegar(self):
        t = make_raw(prioridad="Urgente", proyecto="Marketing")
        assert EisenhowerService.clasificar(t) == "Q3"

    def test_baja_mas_soporte_es_q4_posponer(self):
        t = make_raw(prioridad="Baja", proyecto="Soporte")
        assert EisenhowerService.clasificar(t) == "Q4"

    def test_usa_eisenhower_de_la_api_si_esta_presente(self):
        t = make_raw(eisenhower="Q2")
        assert EisenhowerService.clasificar(t) == "Q2"


class TestAgruparEnCuadrantes:
    def test_excluye_completadas(self):
        svc = EisenhowerService()
        tareas = [
            make_raw(id=1, estado="En Proceso", prioridad="Urgente", proyecto="Desarrollo"),
            make_raw(id=2, estado="Completado", prioridad="Urgente", proyecto="Desarrollo"),
        ]
        quads = svc.agrupar_en_cuadrantes(tareas)
        assert len(quads["Q1"]) == 1
