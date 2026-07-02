import pytest

from domain.entities import RiskScore


class TestRiskScore:
    def test_calcular(self):
        rs = RiskScore(0.8, 0.9, 0.2)
        assert rs.calcular() == pytest.approx(0.576)

    def test_nivel_critico_cuando_score_mayor_igual_050(self):
        rs = RiskScore(0.8, 0.9, 0.2)
        assert rs.nivel() == "crítico"

    def test_nivel_medio_en_rango_015_a_030(self):
        rs = RiskScore(0.7, 0.6, 0.3)
        assert rs.calcular() == pytest.approx(0.294)
        assert rs.nivel() == "medio"

    def test_nivel_bajo_cuando_score_menor_015(self):
        rs = RiskScore(0.1, 0.1, 0.9)
        assert rs.nivel() == "bajo"

    def test_calcular_cero_cuando_cobertura_total(self):
        rs = RiskScore(1, 1, 1)
        assert rs.calcular() == 0

    def test_from_raw_score_cero(self):
        rs = RiskScore.from_raw_score(0)
        assert rs.calcular() == 0
