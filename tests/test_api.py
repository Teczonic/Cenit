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
