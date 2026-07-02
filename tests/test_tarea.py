from datetime import datetime, timedelta

from domain.entities import Tarea, Usuario


def make_tarea(**overrides) -> Tarea:
    base = dict(
        id=1,
        descripcion="Test task",
        entidad="Xertify",
        proyecto="Desarrollo",
        cliente=None,
        responsable=None,
        prioridad="Media",
        estado="No Iniciado",
        fecha_inicio=None,
        fecha_fin=None,
        comentarios=None,
        risk_score=0,
    )
    base.update(overrides)
    return Tarea(**base)


class TestTarea:
    def test_mover_estado_actualiza_el_estado(self):
        t = make_tarea()
        t.mover_estado("En Proceso")
        assert t.estado == "En Proceso"

    def test_esta_vencida_true_con_fecha_fin_pasada_y_no_completada(self):
        ayer = datetime.now() - timedelta(days=1)
        t = make_tarea(fecha_fin=ayer, estado="En Proceso")
        assert t.esta_vencida() is True

    def test_esta_vencida_false_cuando_estado_completado(self):
        ayer = datetime.now() - timedelta(days=1)
        t = make_tarea(fecha_fin=ayer, estado="Completado")
        assert t.esta_vencida() is False

    def test_esta_vencida_false_sin_fecha_fin(self):
        t = make_tarea(fecha_fin=None)
        assert t.esta_vencida() is False

    def test_asignar_responsable_actualiza_responsable(self):
        t = make_tarea()
        usuario = Usuario(id=1, username="fidel", nombre="Fidel López", rol="admin", color="#fff")
        t.asignar_responsable(usuario)
        assert t.responsable == "Fidel López"

    def test_calcular_riesgo_retorna_riskscore_valido(self):
        t = make_tarea(risk_score=50)
        rs = t.calcular_riesgo()
        assert rs.calcular() > 0
