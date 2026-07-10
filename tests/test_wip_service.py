"""Tests del WipService — límites WIP puros, sin base de datos."""

from domain.services import WipService

COLUMNAS = [
    {"estado": "No Iniciado", "wip_limit": None, "wip_limit_scope": "board"},
    {"estado": "En Proceso", "wip_limit": 3, "wip_limit_scope": "board"},
    {"estado": "Pausado", "wip_limit": 2, "wip_limit_scope": "person"},
]


def _t(tid, estado, responsable=None, fecha_inicio=None):
    return {"id": tid, "estado": estado, "responsable": responsable,
            "descripcion": f"Tarea {tid}", "fecha_inicio": fecha_inicio,
            "created_at": None}


class TestOcupacion:
    def test_columna_sin_limite(self):
        wip = WipService().ocupacion([_t(1, "No Iniciado")], COLUMNAS)
        assert wip["No Iniciado"]["status"] == "sin_limite"
        assert wip["No Iniciado"]["ocupacion"] == 1

    def test_bajo_el_limite_es_ok(self):
        tareas = [_t(1, "En Proceso"), _t(2, "En Proceso")]
        wip = WipService().ocupacion(tareas, COLUMNAS)
        assert wip["En Proceso"]["status"] == "ok"

    def test_en_el_limite_es_al_limite(self):
        tareas = [_t(i, "En Proceso") for i in range(3)]
        assert WipService().ocupacion(tareas, COLUMNAS)["En Proceso"]["status"] == "al_limite"

    def test_sobre_el_limite_es_excedido(self):
        tareas = [_t(i, "En Proceso") for i in range(4)]
        wip = WipService().ocupacion(tareas, COLUMNAS)
        assert wip["En Proceso"]["status"] == "excedido"
        assert wip["En Proceso"]["ocupacion"] == 4

    def test_scope_persona_manda_la_mas_cargada(self):
        # 3 tareas de Ana en Pausado (límite 2 por persona) → excedido,
        # aunque el total del tablero sea bajo
        tareas = [_t(1, "Pausado", "Ana"), _t(2, "Pausado", "Ana"),
                  _t(3, "Pausado", "Ana"), _t(4, "Pausado", "Beto")]
        wip = WipService().ocupacion(tareas, COLUMNAS)
        assert wip["Pausado"]["status"] == "excedido"
        assert wip["Pausado"]["por_persona"] == {"Ana": 3, "Beto": 1}

    def test_sin_responsable_cuenta_como_sin_asignar(self):
        tareas = [_t(1, "Pausado"), _t(2, "Pausado")]
        wip = WipService().ocupacion(tareas, COLUMNAS)
        assert wip["Pausado"]["por_persona"] == {"Sin asignar": 2}
        assert wip["Pausado"]["status"] == "al_limite"


class TestEvaluarMovimiento:
    def test_columna_sin_limite_nunca_excede(self):
        v = WipService().evaluar_movimiento([], COLUMNAS, "No Iniciado")
        assert v["excedido"] is False
        assert v["wip_limit"] is None

    def test_movimiento_que_cabe_no_excede(self):
        tareas = [_t(1, "En Proceso"), _t(2, "En Proceso")]
        v = WipService().evaluar_movimiento(tareas, COLUMNAS, "En Proceso")
        assert v["excedido"] is False  # 2 + 1 = 3 ≤ límite 3

    def test_movimiento_que_rompe_el_limite(self):
        tareas = [_t(i, "En Proceso") for i in range(3)]
        v = WipService().evaluar_movimiento(tareas, COLUMNAS, "En Proceso")
        assert v["excedido"] is True
        assert v["wip_actual"] == 3
        assert v["wip_limit"] == 3

    def test_sugiere_las_mas_antiguas_primero(self):
        tareas = [
            _t(1, "En Proceso", fecha_inicio="2026-07-01"),
            _t(2, "En Proceso", fecha_inicio="2026-06-01"),
            _t(3, "En Proceso", fecha_inicio="2026-06-15"),
        ]
        v = WipService().evaluar_movimiento(tareas, COLUMNAS, "En Proceso")
        assert [a["id"] for a in v["tareas_mas_antiguas"]] == [2, 3, 1]

    def test_scope_persona_solo_cuenta_al_responsable(self):
        tareas = [_t(1, "Pausado", "Ana"), _t(2, "Pausado", "Ana"),
                  _t(3, "Pausado", "Beto")]
        # Ana ya tiene 2 (límite por persona) → su tercera excede
        v = WipService().evaluar_movimiento(tareas, COLUMNAS, "Pausado", responsable="Ana")
        assert v["excedido"] is True
        assert v["wip_actual"] == 2
        # Beto tiene 1 → todavía cabe
        v = WipService().evaluar_movimiento(tareas, COLUMNAS, "Pausado", responsable="Beto")
        assert v["excedido"] is False
