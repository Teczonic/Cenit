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
