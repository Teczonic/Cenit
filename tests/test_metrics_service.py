from domain.metrics import MetricsEngine, evaluar_estado, tendencia


class TestEvaluarEstadoUp:
    d = {"direccion": "up", "meta": 85, "umbral_alerta": 60}

    def test_verde_en_o_sobre_meta(self):
        assert evaluar_estado(self.d, 85) == "verde"
        assert evaluar_estado(self.d, 90) == "verde"

    def test_ambar_entre_umbral_y_meta(self):
        assert evaluar_estado(self.d, 70) == "ambar"

    def test_rojo_bajo_umbral(self):
        assert evaluar_estado(self.d, 55) == "rojo"


class TestEvaluarEstadoDown:
    d = {"direccion": "down", "meta": 5, "umbral_alerta": 10}

    def test_verde_en_o_bajo_meta(self):
        assert evaluar_estado(self.d, 5) == "verde"
        assert evaluar_estado(self.d, 3) == "verde"

    def test_ambar_entre_meta_y_umbral(self):
        assert evaluar_estado(self.d, 7) == "ambar"

    def test_rojo_sobre_umbral(self):
        assert evaluar_estado(self.d, 12) == "rojo"


class TestEvaluarEstadoBand:
    d = {"direccion": "band", "banda_min": 1, "banda_max": 3}

    def test_verde_dentro_de_banda(self):
        assert evaluar_estado(self.d, 2) == "verde"
        assert evaluar_estado(self.d, 1) == "verde"
        assert evaluar_estado(self.d, 3) == "verde"

    def test_rojo_fuera_de_banda(self):
        assert evaluar_estado(self.d, 4) == "rojo"
        assert evaluar_estado(self.d, 0) == "rojo"


class TestEvaluarEstadoBordes:
    def test_sin_valor_es_sin_datos(self):
        assert evaluar_estado({"direccion": "up", "meta": 5}, None) == "sin_datos"

    def test_sin_meta_es_sin_datos(self):
        assert evaluar_estado({"direccion": "up"}, 10) == "sin_datos"

    def test_up_sin_umbral_nunca_es_rojo(self):
        assert evaluar_estado({"direccion": "up", "meta": 10}, 2) == "ambar"


class TestTendencia:
    def test_sube(self):
        snaps = [{"periodo_inicio": "2026-01-01", "periodo_fin": "2026-01-07", "valor": 5},
                 {"periodo_inicio": "2026-01-08", "periodo_fin": "2026-01-14", "valor": 8}]
        assert tendencia(snaps) == "sube"

    def test_baja(self):
        snaps = [{"periodo_inicio": "2026-01-01", "periodo_fin": "2026-01-07", "valor": 8},
                 {"periodo_inicio": "2026-01-08", "periodo_fin": "2026-01-14", "valor": 5}]
        assert tendencia(snaps) == "baja"

    def test_estable(self):
        snaps = [{"periodo_inicio": "2026-01-01", "periodo_fin": "2026-01-07", "valor": 5},
                 {"periodo_inicio": "2026-01-08", "periodo_fin": "2026-01-14", "valor": 5}]
        assert tendencia(snaps) == "estable"

    def test_un_solo_snapshot_es_none(self):
        assert tendencia([{"periodo_inicio": "2026-01-01", "periodo_fin": "2026-01-07", "valor": 5}]) is None


class TestMetricsEngine:
    def test_resumir_toma_ultimo_valor_y_estado(self):
        engine = MetricsEngine()
        d = {"direccion": "down", "meta": 5, "umbral_alerta": 10}
        snaps = [{"periodo_inicio": "2026-01-01", "periodo_fin": "2026-01-07", "valor": 9, "estado": "ambar"},
                 {"periodo_inicio": "2026-01-08", "periodo_fin": "2026-01-14", "valor": 4, "estado": "verde"}]
        res = engine.resumir(d, snaps)
        assert res["valor_actual"] == 4
        assert res["estado"] == "verde"
        assert res["tendencia"] == "baja"
        assert len(res["historial"]) == 2
