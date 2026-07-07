"""Cliente HTTP hacia la API FastAPI de Cenit (equivalente Python de lib/api.ts)."""

from __future__ import annotations

import os
from typing import Optional

import requests


class ApiError(Exception):
    pass


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
            raise ApiError(f"{res.status_code}: {detail}")
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

    def patch_status(self, task_id: int, estado: str) -> dict:
        return self._request("PATCH", f"/api/tasks/{task_id}/status",
                             json={"estado": estado})

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
