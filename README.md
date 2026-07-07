# 🏔️ Cenit — Team Backlog Manager

App para gestionar el backlog del equipo Xertify/Xertiflow, **100% Python**,
alineada con el roadmap *Builder de Productos Digitales* (Platzi · Teczonic).

## Stack

| Capa | Tecnología | Curso del roadmap |
|---|---|---|
| API | **FastAPI** + Pydantic + JWT | Curso de FastAPI |
| UI | **Streamlit** (dashboards en Python puro) | Curso de Streamlit |
| Datos | **SQLAlchemy** → PostgreSQL (Supabase) / SQLite local | Curso de SQL con Python |
| Dominio | Paquete `domain/` sin dependencias de framework | Curso de Python: POO |
| Tests | **pytest** (unitarios + integración con TestClient) | Curso de Testing con Pytest |
| CI | **GitHub Actions** (pytest en cada push/PR) | Curso de CI/CD |
| Deploy | **Docker Compose** (db + api + ui) | Curso de Docker |

## Estructura

```
├── api/          # FastAPI: endpoints, modelos SQLAlchemy, auth JWT, CRUD
├── domain/       # Lógica de negocio pura: entidades y servicios (testeable sin nada más)
├── ui/           # Streamlit: app.py (login + navegación) y views/ (una por página)
├── tests/        # pytest: dominio + API con TestClient
├── Dockerfile.api / Dockerfile.ui / docker-compose.yml
└── .github/workflows/ci.yml
```

## Desarrollo local

```bash
# 1. Instalar dependencias
pip install -r requirements-dev.txt

# 2. Levantar la API (terminal 1) — usa SQLite local si no hay DATABASE_URL
uvicorn api.main:app --reload

# 3. Levantar la UI (terminal 2)
streamlit run ui/app.py

# 4. Correr los tests
pytest
```

La API siembra usuarios y tareas de ejemplo en el primer arranque
(login de prueba: `fidel` / `fidel123`).

## Con Docker (db + api + ui)

```bash
docker compose up --build
# UI:  http://localhost:8501
# API: http://localhost:8000/docs
```

`SECRET_KEY`, `POSTGRES_USER` y `POSTGRES_PASSWORD` se leen de variables
de entorno (o un archivo `.env` junto al compose) — no las dejes por defecto
en producción.

## Deploy

Guía paso a paso en [DEPLOY.md](DEPLOY.md). Resumen:

- **API** → Vercel (`api/index.py` vía `@vercel/python`, ver `vercel.json`).
  `vercel.json` enruta todo a la función, así que la raíz, `/docs` y `/api/*`
  responden. Requiere `DATABASE_URL` (Supabase) y `SECRET_KEY` como env vars;
  tras el deploy, `POST /api/seed` siembra datos. Salud en `/api/health`.
- **UI** → Streamlit Community Cloud (o Railway/Render/Fly.io con `Dockerfile.ui`),
  con `CENIT_API_URL` apuntando a la API. Streamlit **no** corre en Vercel.
- Variables de entorno de referencia en [.env.example](.env.example).

## Vistas

- **Cockpit** — la superficie del líder: qué está en riesgo, qué está lento y qué
  decidir hoy. Combina el motor de flujo (lead time real, cycle time, aging, flow
  efficiency), el de riesgo, la alineación de OKR y recomendaciones basadas en reglas.
- **Mi día** — tus tareas agrupadas: vencidas, para hoy, próximas, en curso.
- **OKRs** — dirección del trimestre: objetivos, key results con progreso calculado
  y alineación (% de tareas abiertas vinculadas a un resultado).
- **KPIs** — motor de métricas: cada indicador con meta, umbral y semáforo
  verde/ámbar/rojo, más tendencia e historial de mediciones.
- **Kanban** — 4 columnas por estado, mover tareas entre estados.
- **Eisenhower** — matriz 2×2 importante/urgente (excluye completadas).
- **Riesgos** — top 30 por `risk_score` (probabilidad × impacto × (1 − cobertura)).
- **Analytics** — métricas, throughput mensual, lead time por persona.
- **Equipo** — carga por responsable; los admins crean usuarios.
- **Importar CSV** — sube un export de Jira/Trello/Excel; Cenit detecta las columnas
  y crea las tareas, habilitando el diagnóstico inmediato en el Cockpit.

## Motor de flujo

Cada cambio de estado se registra en `task_state_transitions`. Sobre ese historial,
`domain/services.py::FlowService` calcula lead time real, cycle time, flow efficiency
(tiempo activo vs pausado) y aging. Expuesto en `GET /api/analytics/flow` y en
`GET /api/tasks/{id}/transitions`. Es el cimiento del cockpit y de las métricas
futuras (DORA, Lean) — la ventaja de Cenit está en la memoria histórica.

## Dirección (OKRs)

`okr_cycles → objectives → key_results`, con `task_key_results` vinculando tareas a
resultados. `domain/okrs.py::OkrService` calcula el progreso de cada KR (fracción
recorrida entre valor inicial y meta, sirve para metas ascendentes y descendentes),
el de cada objetivo (promedio de sus KRs) y el *alignment ratio* (% de tareas
abiertas conectadas a un KR). Expuesto en `GET /api/okr/overview` y consumido por el
cockpit — conecta el trabajo diario con el resultado del trimestre.

## Motor de métricas (KPIs)

`metric_definitions` (catálogo con meta/umbral/dirección) + `metric_snapshots`
(serie temporal inmutable, append-only). `domain/metrics.py` evalúa el semáforo
—`up` (más es mejor), `down` (menos es mejor), `band` (rango objetivo)— y la
tendencia entre snapshots. Expuesto en `GET /api/kpis/overview`. La regla de diseño
(ver `docs/arquitectura`): **una métrica es un dato, no un módulo** — DORA, SPACE y
los KRs cuantitativos se montarán como filas de este motor, sin duplicar lógica de
semáforo, snapshot ni UI.
