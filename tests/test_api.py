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
        # force=True: el seed real ya excede el límite WIP de «En Proceso»
        client.patch(f"/api/tasks/{task_id}/status",
                     json={"estado": "En Proceso", "force": True}, headers=auth(token))
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


class TestWipLimits:
    def test_columnas_por_defecto(self, client):
        res = client.get("/api/kanban/columns")
        assert res.status_code == 200
        cols = {c["estado"]: c for c in res.json()}
        assert cols["En Proceso"]["wip_limit"] == 10
        assert cols["No Iniciado"]["wip_limit"] is None
        assert cols["En Proceso"]["policy_text"]

    def test_wip_status_reporta_ocupacion(self, client):
        res = client.get("/api/kanban/wip-status")
        assert res.status_code == 200
        wip = res.json()["wip"]
        assert wip["En Proceso"]["ocupacion"] >= 1
        assert wip["En Proceso"]["status"] in ("ok", "al_limite", "excedido")
        assert wip["Completado"]["status"] == "sin_limite"

    def test_editar_limite_requiere_token(self, client):
        res = client.put("/api/kanban/columns/En Proceso", json={"wip_limit": 5})
        assert res.status_code == 401

    def test_editar_limite_con_member_da_403(self, client):
        tk = client.post("/api/auth/login",
                         json={"username": "moshe", "password": "Moshe21"}).json()["token"]
        res = client.put("/api/kanban/columns/En Proceso", json={"wip_limit": 5}, headers=auth(tk))
        assert res.status_code == 403

    def test_scope_invalido_da_400(self, client, token):
        res = client.put("/api/kanban/columns/En Proceso",
                         json={"wip_limit": 5, "wip_limit_scope": "galaxia"}, headers=auth(token))
        assert res.status_code == 400

    def test_mover_a_columna_llena_da_409_y_force_lo_permite(self, client, token):
        # Bajar el límite a 1 garantiza el conflicto (el seed ya tiene tareas En Proceso)
        res = client.put("/api/kanban/columns/En Proceso",
                         json={"wip_limit": 1, "wip_limit_scope": "board"}, headers=auth(token))
        assert res.status_code == 200

        nueva = client.post("/api/tasks",
                            json={"entidad": "Xertify", "descripcion": "Tarea WIP test",
                                  "estado": "No Iniciado"}, headers=auth(token)).json()
        res = client.patch(f'/api/tasks/{nueva["id"]}/status',
                           json={"estado": "En Proceso"}, headers=auth(token))
        assert res.status_code == 409
        detalle = res.json()["detail"]
        assert detalle["wip_limit"] == 1
        assert detalle["excedido"] is True
        assert detalle["tareas_mas_antiguas"]  # sugiere terminar antes de empezar

        # Persuade, no bloquea: con force el movimiento procede y queda en el historial
        res = client.patch(f'/api/tasks/{nueva["id"]}/status',
                           json={"estado": "En Proceso", "force": True}, headers=auth(token))
        assert res.status_code == 200
        assert res.json()["estado"] == "En Proceso"
        trans = client.get(f'/api/tasks/{nueva["id"]}/transitions').json()
        assert [t["to_state"] for t in trans] == ["No Iniciado", "En Proceso"]

        # Restaurar el límite por defecto para no contaminar otros tests
        res = client.put("/api/kanban/columns/En Proceso",
                         json={"wip_limit": 10, "wip_limit_scope": "board"}, headers=auth(token))
        assert res.status_code == 200

    def test_mover_dentro_de_la_misma_columna_no_choca_con_wip(self, client, token):
        # Repetir el estado actual no debe disparar el 409 aunque la columna esté llena
        tarea = client.get("/api/tasks", params={"status": "En Proceso"}).json()[0]
        res = client.patch(f'/api/tasks/{tarea["id"]}/status',
                           json={"estado": "En Proceso"}, headers=auth(token))
        assert res.status_code == 200


class TestLean:
    def test_resumen_lean_estructura(self, client):
        res = client.get("/api/analytics/lean")
        assert res.status_code == 200
        body = res.json()
        for clave in ("pareto", "detecciones", "bloqueos_activos",
                      "tareas_zombi", "little", "tasa_retrabajo"):
            assert clave in body
        assert body["little"]["wip_actual"] > 0  # el seed tiene WIP

    def test_reportar_bloqueo_requiere_token(self, client):
        res = client.post("/api/tasks/1/waste", json={"waste_type": "espera"})
        assert res.status_code == 401

    def test_waste_type_invalido_da_400(self, client, token):
        tarea = client.get("/api/tasks").json()[0]
        res = client.post(f'/api/tasks/{tarea["id"]}/waste',
                          json={"waste_type": "aburrimiento"}, headers=auth(token))
        assert res.status_code == 400

    def test_reportar_y_resolver_bloqueo(self, client, token):
        tarea = client.get("/api/tasks", params={"status": "En Proceso"}).json()[0]
        w = client.post(f'/api/tasks/{tarea["id"]}/waste',
                        json={"waste_type": "espera", "descripcion": "Esperando al cliente"},
                        headers=auth(token)).json()
        assert w["reported_by"] == "fidel"
        assert w["resolved_at"] is None

        # Aparece como bloqueo activo en el resumen
        lean = client.get("/api/analytics/lean").json()
        assert any(b["id"] == w["id"] for b in lean["bloqueos_activos"])
        assert any(p["waste_type"] == "espera" for p in lean["pareto"])

        # Resolver lo saca de los activos
        r = client.patch(f'/api/waste/{w["id"]}/resolve', headers=auth(token)).json()
        assert r["resolved_at"] is not None
        lean = client.get("/api/analytics/lean").json()
        assert not any(b["id"] == w["id"] for b in lean["bloqueos_activos"])

    def test_seed_detecta_desperdicio_automatico(self, client):
        # El seed tiene pausas viejas y responsables cargados: la detección
        # automática debe encontrar algo sin que nadie reporte nada
        lean = client.get("/api/analytics/lean").json()
        assert len(lean["detecciones"]) > 0


class TestSprints:
    def test_seed_trae_sprint_activo_con_detalle(self, client):
        sprints = client.get("/api/sprints", params={"estado": "activo"}).json()
        assert len(sprints) >= 1
        detalle = client.get(f'/api/sprints/{sprints[0]["id"]}').json()
        assert detalle["velocity"]["puntos_comprometidos"] > 0
        assert "burndown" in detalle

    def test_crear_sprint_requiere_token(self, client):
        res = client.post("/api/sprints", json={
            "nombre": "X", "entidad": "Xertify",
            "fecha_inicio": "2026-08-01", "fecha_fin": "2026-08-14"})
        assert res.status_code == 401

    def test_fechas_invalidas_dan_400(self, client, token):
        res = client.post("/api/sprints", json={
            "nombre": "Fechas mal", "entidad": "Xertify",
            "fecha_inicio": "2026-08-14", "fecha_fin": "2026-08-01"}, headers=auth(token))
        assert res.status_code == 400

    def test_story_points_no_fibonacci_da_400(self, client, token):
        res = client.post("/api/tasks", json={
            "entidad": "Xertify", "descripcion": "Puntos raros", "story_points": 4,
        }, headers=auth(token))
        assert res.status_code == 400

    def test_solo_un_sprint_activo_por_entidad(self, client, token):
        nuevo = client.post("/api/sprints", json={
            "nombre": "Sprint doble", "entidad": "Xertify",
            "fecha_inicio": "2026-08-01", "fecha_fin": "2026-08-14"},
            headers=auth(token)).json()
        res = client.patch(f'/api/sprints/{nuevo["id"]}', json={"estado": "activo"},
                           headers=auth(token))
        assert res.status_code == 409  # ya hay un sprint activo en Xertify (seed)

    def test_comprometer_tarea_sin_puntos_da_400(self, client, token):
        sprint = client.post("/api/sprints", json={
            "nombre": "Sprint puntos", "entidad": "Xertiflow",
            "fecha_inicio": "2026-08-01", "fecha_fin": "2026-08-14"},
            headers=auth(token)).json()
        tarea = client.post("/api/tasks", json={
            "entidad": "Xertiflow", "descripcion": "Sin estimar"}, headers=auth(token)).json()
        res = client.post(f'/api/sprints/{sprint["id"]}/tasks',
                          json={"task_ids": [tarea["id"]]}, headers=auth(token))
        assert res.status_code == 400
        assert tarea["id"] in res.json()["detail"]["sin_puntos"]

    def test_ciclo_completo_comprometer_activar_cerrar(self, client, token):
        sprint = client.post("/api/sprints", json={
            "nombre": "Sprint ciclo", "entidad": "Xertiflow",
            "fecha_inicio": "2026-06-01", "fecha_fin": "2026-06-12"},
            headers=auth(token)).json()

        hecha = client.post("/api/tasks", json={
            "entidad": "Xertiflow", "descripcion": "Se completa", "story_points": 5,
            "estado": "En Proceso"}, headers=auth(token)).json()
        pendiente = client.post("/api/tasks", json={
            "entidad": "Xertiflow", "descripcion": "Queda pendiente", "story_points": 3,
        }, headers=auth(token)).json()

        res = client.post(f'/api/sprints/{sprint["id"]}/tasks',
                          json={"task_ids": [hecha["id"], pendiente["id"]]}, headers=auth(token))
        assert res.status_code == 200
        assert res.json()["committed"] is True  # en planning comprometen
        assert res.json()["puntos"] == 8

        client.patch(f'/api/sprints/{sprint["id"]}', json={"estado": "activo"}, headers=auth(token))
        client.patch(f'/api/tasks/{hecha["id"]}/status',
                     json={"estado": "Completado"}, headers=auth(token))

        cierre = client.post(f'/api/sprints/{sprint["id"]}/close', headers=auth(token)).json()
        # fecha_fin del sprint quedó en el pasado; la tarea se completó hoy →
        # fuera de ventana. Solo valida la estructura del reporte:
        assert cierre["puntos_comprometidos"] == 8
        assert "carryover_sugerido" in cierre
        assert "say_do_ratio" in cierre

        detalle = client.get(f'/api/sprints/{sprint["id"]}').json()
        assert detalle["estado"] == "cerrado"

        # El histórico de velocity ya lo incluye
        hist = client.get("/api/analytics/velocity", params={"entidad": "Xertiflow"}).json()
        assert hist["sprints"] >= 1

    def test_cerrar_requiere_creador_o_admin(self, client, token):
        sprint = client.post("/api/sprints", json={
            "nombre": "Sprint permisos", "entidad": "Xertiflow",
            "fecha_inicio": "2026-09-01", "fecha_fin": "2026-09-12"},
            headers=auth(token)).json()
        tk_member = client.post("/api/auth/login",
                                json={"username": "moshe", "password": "Moshe21"}).json()["token"]
        res = client.post(f'/api/sprints/{sprint["id"]}/close', headers=auth(tk_member))
        assert res.status_code == 403


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
