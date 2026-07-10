"""Cliente HTTP hacia la API FastAPI de Cenit (equivalente Python de lib/api.ts)."""

from __future__ import annotations

import os
from typing import Optional

import requests


class ApiError(Exception):
    """Error de la API. Cuando el detail es estructurado (p. ej. el veredicto
    WIP de un 409), queda disponible en `payload` junto al `status_code`."""

    def __init__(self, message: str, status_code: Optional[int] = None, payload: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


def get_base_url() -> str:
    return os.getenv("CENIT_API_URL", "http://localhost:8000").rstrip("/")


class CenitClient:
    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        self.base_url = base_url or get_base_url()
        self.token = token

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _request(self, method: str, path: str, **kwargs):
        try:
            res = requests.request(
                method, f"{self.base_url}{path}", headers=self._headers(),
                timeout=15, **kwargs,
            )
        except requests.ConnectionError as e:
            raise ApiError(f"No se pudo conectar a la API en {self.base_url}: {e}")
        if not res.ok:
            try:
                detail = res.json().get("detail", res.text)
            except ValueError:
                detail = res.text
            if isinstance(detail, dict):
                raise ApiError(f'{res.status_code}: {detail.get("mensaje", detail)}',
                               status_code=res.status_code, payload=detail)
            raise ApiError(f"{res.status_code}: {detail}", status_code=res.status_code)
        return res.json()

    # ── Auth ─────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> dict:
        data = self._request("POST", "/api/auth/login",
                             json={"username": username, "password": password})
        self.token = data["token"]
        return data

    def me(self) -> dict:
        return self._request("GET", "/api/auth/me")

    # ── Users ────────────────────────────────────────────────────────

    def get_users(self) -> list[dict]:
        return self._request("GET", "/api/users")

    def create_user(self, username: str, name: str, password: str,
                    role: str = "member", color: str = "#2563EB") -> dict:
        return self._request("POST", "/api/users", json={
            "username": username, "name": name, "password": password,
            "role": role, "color": color,
        })

    # ── Tasks ────────────────────────────────────────────────────────

    def get_tasks(self, **filters) -> list[dict]:
        params = {k: v for k, v in filters.items() if v}
        return self._request("GET", "/api/tasks", params=params)

    def create_task(self, data: dict) -> dict:
        return self._request("POST", "/api/tasks", json=data)

    def update_task(self, task_id: int, data: dict) -> dict:
        return self._request("PUT", f"/api/tasks/{task_id}", json=data)

    def delete_task(self, task_id: int) -> dict:
        return self._request("DELETE", f"/api/tasks/{task_id}")

    def patch_status(self, task_id: int, estado: str, force: bool = False) -> dict:
        return self._request("PATCH", f"/api/tasks/{task_id}/status",
                             json={"estado": estado, "force": force})

    # ── Kanban: límites WIP ──────────────────────────────────────────

    def kanban_columns(self) -> list[dict]:
        return self._request("GET", "/api/kanban/columns")

    def update_kanban_column(self, estado: str, wip_limit=None,
                             wip_limit_scope=None, policy_text=None) -> dict:
        return self._request("PUT", f"/api/kanban/columns/{estado}", json={
            "wip_limit": wip_limit, "wip_limit_scope": wip_limit_scope,
            "policy_text": policy_text,
        })

    def wip_status(self) -> dict:
        return self._request("GET", "/api/kanban/wip-status")

    # ── Sprints ──────────────────────────────────────────────────────

    def sprints(self, entidad: str | None = None, estado: str | None = None) -> list[dict]:
        params = {k: v for k, v in {"entidad": entidad, "estado": estado}.items() if v}
        return self._request("GET", "/api/sprints", params=params)

    def create_sprint(self, data: dict) -> dict:
        return self._request("POST", "/api/sprints", json=data)

    def sprint_detail(self, sprint_id: int) -> dict:
        return self._request("GET", f"/api/sprints/{sprint_id}")

    def patch_sprint(self, sprint_id: int, data: dict) -> dict:
        return self._request("PATCH", f"/api/sprints/{sprint_id}", json=data)

    def add_sprint_tasks(self, sprint_id: int, task_ids: list[int]) -> dict:
        return self._request("POST", f"/api/sprints/{sprint_id}/tasks",
                             json={"task_ids": task_ids})

    def remove_sprint_task(self, sprint_id: int, task_id: int) -> dict:
        return self._request("DELETE", f"/api/sprints/{sprint_id}/tasks/{task_id}")

    def close_sprint(self, sprint_id: int) -> dict:
        return self._request("POST", f"/api/sprints/{sprint_id}/close")

    def sprint_burndown(self, sprint_id: int) -> dict:
        return self._request("GET", f"/api/sprints/{sprint_id}/burndown")

    def analytics_velocity(self, entidad: str | None = None, n: int = 6) -> dict:
        params = {"n": n}
        if entidad:
            params["entidad"] = entidad
        return self._request("GET", "/api/analytics/velocity", params=params)

    # ── Analytics ────────────────────────────────────────────────────

    def analytics_summary(self) -> dict:
        return self._request("GET", "/api/analytics/summary")

    def analytics_throughput(self) -> list[dict]:
        return self._request("GET", "/api/analytics/throughput")

    def analytics_lead_time(self) -> list[dict]:
        return self._request("GET", "/api/analytics/lead_time")

    def analytics_flow(self) -> dict:
        return self._request("GET", "/api/analytics/flow")

    def task_transitions(self, task_id: int) -> list[dict]:
        return self._request("GET", f"/api/tasks/{task_id}/transitions")

    # ── OKRs ─────────────────────────────────────────────────────────

    def okr_cycles(self) -> list[dict]:
        return self._request("GET", "/api/okr/cycles")

    def create_okr_cycle(self, nombre: str, fecha_inicio: str, fecha_fin: str) -> dict:
        return self._request("POST", "/api/okr/cycles", json={
            "nombre": nombre, "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})

    def okr_overview(self, cycle_id: int | None = None) -> dict:
        params = {"cycle_id": cycle_id} if cycle_id else {}
        return self._request("GET", "/api/okr/overview", params=params)

    def create_objective(self, cycle_id: int, titulo: str, owner=None, entidad=None) -> dict:
        return self._request("POST", "/api/okr/objectives", json={
            "cycle_id": cycle_id, "titulo": titulo, "owner": owner, "entidad": entidad})

    def create_key_result(self, objective_id: int, titulo: str, valor_inicial: float,
                          valor_meta: float, valor_actual: float = 0, unidad=None) -> dict:
        return self._request("POST", "/api/okr/key-results", json={
            "objective_id": objective_id, "titulo": titulo, "valor_inicial": valor_inicial,
            "valor_meta": valor_meta, "valor_actual": valor_actual, "unidad": unidad})

    def patch_kr(self, kr_id: int, valor_actual: float) -> dict:
        return self._request("PATCH", f"/api/okr/key-results/{kr_id}",
                             json={"valor_actual": valor_actual})

    def link_task_kr(self, task_id: int, kr_id: int) -> dict:
        return self._request("POST", f"/api/tasks/{task_id}/key-results/{kr_id}")

    # ── KPIs ─────────────────────────────────────────────────────────

    def kpi_overview(self, entidad: str | None = None) -> dict:
        params = {"entidad": entidad} if entidad else {}
        return self._request("GET", "/api/kpis/overview", params=params)

    def create_kpi(self, data: dict) -> dict:
        return self._request("POST", "/api/kpis", json=data)

    def add_measurement(self, metric_id: int, periodo_inicio: str,
                        periodo_fin: str, valor: float) -> dict:
        return self._request("POST", f"/api/kpis/{metric_id}/measurements", json={
            "periodo_inicio": periodo_inicio, "periodo_fin": periodo_fin, "valor": valor})
