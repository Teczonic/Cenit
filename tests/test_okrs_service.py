from domain.okrs import OkrService


class TestProgresoKR:
    svc = OkrService()

    def test_progreso_ascendente(self):
        kr = {"valor_inicial": 0, "valor_meta": 100, "valor_actual": 40}
        assert self.svc.progreso_kr(kr) == 0.4

    def test_progreso_descendente(self):
        # meta menor que inicial (ej: bajar lead time de 8 a 5, vamos en 7)
        kr = {"valor_inicial": 8, "valor_meta": 5, "valor_actual": 7}
        assert self.svc.progreso_kr(kr) == round(1 / 3, 4)

    def test_progreso_se_satura_entre_0_y_1(self):
        assert self.svc.progreso_kr({"valor_inicial": 0, "valor_meta": 10, "valor_actual": 25}) == 1.0
        assert self.svc.progreso_kr({"valor_inicial": 0, "valor_meta": 10, "valor_actual": -5}) == 0.0

    def test_meta_igual_inicial(self):
        assert self.svc.progreso_kr({"valor_inicial": 5, "valor_meta": 5, "valor_actual": 5}) == 1.0
        assert self.svc.progreso_kr({"valor_inicial": 5, "valor_meta": 5, "valor_actual": 3}) == 0.0


class TestProgresoObjective:
    svc = OkrService()

    def test_promedia_los_krs(self):
        krs = [
            {"valor_inicial": 0, "valor_meta": 100, "valor_actual": 100},  # 1.0
            {"valor_inicial": 0, "valor_meta": 100, "valor_actual": 0},    # 0.0
        ]
        assert self.svc.progreso_objective(krs) == 0.5

    def test_sin_krs_es_cero(self):
        assert self.svc.progreso_objective([]) == 0.0


class TestAlignment:
    svc = OkrService()

    def test_ratio_de_tareas_abiertas_vinculadas(self):
        tareas = [
            {"id": 1, "estado": "En Proceso"},
            {"id": 2, "estado": "No Iniciado"},
            {"id": 3, "estado": "Completado"},  # no cuenta (cerrada)
            {"id": 4, "estado": "Pausado"},
        ]
        # vinculadas: 1 y 3; solo 1 está abierta → 1/3 abiertas = 33.3%
        assert self.svc.alignment_ratio(tareas, {1, 3}) == 33.3

    def test_sin_tareas_abiertas_es_cero(self):
        assert self.svc.alignment_ratio([{"id": 1, "estado": "Completado"}], {1}) == 0.0
