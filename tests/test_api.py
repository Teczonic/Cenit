"""Tests de integración de la API FastAPI con TestClient + SQLite temporal."""

import os

import pytest


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("db") / "test_cenit.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    from fastapi.testclient import TestClient

    from api.main import app

    # El lifespan crea las tablas y siembra los datos iniciales
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def token(client):
    res = client.post("/api/auth/login", json={"username": "fidel", "password": "fidel123"})
    assert res.status_code == 200
    return res.json()["token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


class TestAuth:
    def test_login_ok_devuelve_token_y_usuario(self, client):
        res = client.post("/api/auth/login", json={"username": "moshe", "password": "Moshe21"})
        assert res.status_code == 200
        body = res.json()
        assert body["token"]
        assert body["user"]["username"] == "moshe"

    def test_login_con_password_incorrecta_da_401(self, client):
        res = client.post("/api/auth/login", json={"username": "moshe", "password": "mala"})
        assert res.status_code == 401

    def test_me_requiere_token(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code == 401

    def test_health_reporta_db_arriba(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok", "db": "up"}


class TestTasks:
    def test_listar_tareas_devuelve_seed(self, client):
        res = client.get("/api/tasks")
        assert res.status_code == 200
        tareas = res.json()
        assert len(tareas) > 0
        # Los campos calculados vienen incluidos
        assert "eisenhower" in tareas[0]
        assert "risk_score" in tareas[0]

    def test_crear_tarea_requiere_token(self, client):
        res = client.post("/api/tasks", json={"entidad": "Xertify", "descripcion": "x"})
        assert res.status_code == 401

    def test_crear_y_completar_tarea(self, client, token):
        res = client.post(
            "/api/tasks",
            json={
                "entidad": "Xertify",
                "proyecto": "Desarrollo",
                "descripcion": "Tarea de prueba pytest",
                "prioridad": "Urgente",
                "estado": "En Proceso",
            },
            headers=auth(token),
        )
        assert res.status_code == 200
        tarea = res.json()
        assert tarea["created_by"] == "fidel"
        assert tarea["fecha_inicio"] is not None  # se setea al pasar a En Proceso

        res = client.patch(
            f"/api/tasks/{tarea['id']}/status",
            json={"estado": "Completado"},
            headers=auth(token),
        )
        assert res.status_code == 200
        completada = res.json()
        assert completada["estado"] == "Completado"
        assert completada["fecha_completado"] is not None

    def test_analytics_summary(self, client):
        res = client.get("/api/analytics/summary")
        assert res.status_code == 200
        body = res.json()
        assert body["total"] > 0
        assert "by_prioridad" in body


class TestFlow:
    def test_crear_tarea_registra_transicion_inicial(self, client, token):
        res = client.post(
            "/api/tasks",
            json={"entidad": "Xertify", "descripcion": "Flujo inicial", "estado": "No Iniciado"},
            headers=auth(token),
        )
        task_id = res.json()["id"]
        trans = client.get(f"/api/tasks/{task_id}/transitions").json()
        assert len(trans) == 1
        assert trans[0]["from_state"] is None
        assert trans[0]["to_state"] == "No Iniciado"

    def test_mover_estado_agrega_transiciones_ordenadas(self, client, token):
        res = client.post(
            "/api/tasks",
            json={"entidad": "Xertify", "descripcion": "Flujo movido", "estado": "No Iniciado"},
            headers=auth(token),
        )
        task_id = res.json()["id"]
        client.patch(f"/api/tasks/{task_id}/status", json={"estado": "En Proceso"}, headers=auth(token))
        client.patch(f"/api/tasks/{task_id}/status", json={"estado": "Completado"}, headers=auth(token))

        trans = client.get(f"/api/tasks/{task_id}/transitions").json()
        estados = [t["to_state"] for t in trans]
        assert estados == ["No Iniciado", "En Proceso", "Completado"]
        assert trans[1]["from_state"] == "No Iniciado"
        assert trans[-1]["changed_by"] == "fidel"

    def test_estado_repetido_no_duplica_transicion(self, client, token):
        res = client.post(
            "/api/tasks",
            json={"entidad": "Xertify", "descripcion": "Sin cambio", "estado": "No Iniciado"},
            headers=auth(token),
        )
        task_id = res.json()["id"]
        client.patch(f"/api/tasks/{task_id}/status", json={"estado": "No Iniciado"}, headers=auth(token))
        trans = client.get(f"/api/tasks/{task_id}/transitions").json()
        assert len(trans) == 1  # solo la inicial

    def test_analytics_flow_devuelve_metricas(self, client):
        res = client.get("/api/analytics/flow")
        assert res.status_code == 200
        body = res.json()
        assert body["tareas"] > 0
        assert "lead_time_avg" in body
        assert "por_tarea" in body


class TestOkr:
    def test_overview_trae_objetivos_sembrados(self, client):
        res = client.get("/api/okr/overview")
        assert res.status_code == 200
        body = res.json()
        assert len(body["objectives"]) >= 2
        assert "alignment_ratio" in body
        # cada objetivo trae progreso calculado y sus KRs
        obj = body["objectives"][0]
        assert 0.0 <= obj["progreso"] <= 1.0
        assert isinstance(obj["key_results"], list)

    def test_crear_objetivo_y_kr_requiere_token(self, client):
        res = client.post("/api/okr/objectives", json={"cycle_id": 1, "titulo": "x"})
        assert res.status_code == 401

    def test_flujo_completo_objetivo_kr_y_progreso(self, client, token):
        cycles = client.get("/api/okr/cycles").json()
        cycle_id = cycles[0]["id"]

        obj = client.post("/api/okr/objectives",
                          json={"cycle_id": cycle_id, "titulo": "Objetivo de prueba"},
                          headers=auth(token)).json()
        kr = client.post("/api/okr/key-results",
                         json={"objective_id": obj["id"], "titulo": "KR prueba",
                               "valor_inicial": 0, "valor_meta": 10, "valor_actual": 0},
                         headers=auth(token)).json()
        assert kr["progreso"] == 0.0

        actualizado = client.patch(f'/api/okr/key-results/{kr["id"]}',
                                   json={"valor_actual": 5}, headers=auth(token)).json()
        assert actualizado["progreso"] == 0.5

    def test_vincular_tarea_a_kr_sube_alignment(self, client, token):
        cycle_id = client.get("/api/okr/cycles").json()[0]["id"]
        obj = client.post("/api/okr/objectives",
                          json={"cycle_id": cycle_id, "titulo": "Obj alignment"},
                          headers=auth(token)).json()
        kr = client.post("/api/okr/key-results",
                         json={"objective_id": obj["id"], "titulo": "KR align",
                               "valor_inicial": 0, "valor_meta": 1, "valor_actual": 0},
                         headers=auth(token)).json()
        nueva = client.post("/api/tasks",
                            json={"entidad": "Xertify", "descripcion": "Tarea vinculada",
                                  "estado": "En Proceso"}, headers=auth(token)).json()
        res = client.post(f'/api/tasks/{nueva["id"]}/key-results/{kr["id"]}', headers=auth(token))
        assert res.status_code == 200
        assert res.json()["kr_id"] == kr["id"]


class TestKpis:
    def test_overview_trae_kpis_sembrados_con_semaforo(self, client):
        res = client.get("/api/kpis/overview")
        assert res.status_code == 200
        body = res.json()
        assert len(body["kpis"]) >= 4
        assert set(body["resumen"]) == {"verde", "ambar", "rojo", "sin_datos"}
        k = body["kpis"][0]
        assert k["estado"] in ("verde", "ambar", "rojo", "sin_datos")
        assert "historial" in k

    def test_crear_kpi_requiere_token(self, client):
        res = client.post("/api/kpis", json={"clave": "x", "nombre": "X", "direccion": "up"})
        assert res.status_code == 401

    def test_direccion_invalida_da_400(self, client, token):
        res = client.post("/api/kpis",
                          json={"clave": "bad", "nombre": "Bad", "direccion": "lateral"},
                          headers=auth(token))
        assert res.status_code == 400

    def test_flujo_completo_kpi_medicion_y_semaforo(self, client, token):
        kpi = client.post("/api/kpis", json={
            "clave": "cfr_test", "nombre": "Change failure rate", "direccion": "down",
            "meta": 15, "umbral_alerta": 30, "unidad": "%",
        }, headers=auth(token)).json()

        # Valor bajo la meta → verde
        m1 = client.post(f'/api/kpis/{kpi["id"]}/measurements',
                         json={"periodo_inicio": "2026-06-01", "periodo_fin": "2026-06-07", "valor": 10},
                         headers=auth(token)).json()
        assert m1["estado"] == "verde"

        # Valor sobre el umbral → rojo
        m2 = client.post(f'/api/kpis/{kpi["id"]}/measurements',
                         json={"periodo_inicio": "2026-06-08", "periodo_fin": "2026-06-14", "valor": 35},
                         headers=auth(token)).json()
        assert m2["estado"] == "rojo"

        # El overview refleja el último valor y la tendencia al alza
        ov = client.get("/api/kpis/overview").json()
        cfr = next(k for k in ov["kpis"] if k["clave"] == "cfr_test")
        assert cfr["valor_actual"] == 35
        assert cfr["estado"] == "rojo"
        assert cfr["tendencia"] == "sube"
        assert len(cfr["historial"]) == 2
