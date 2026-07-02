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

- **API** → Vercel (`api/index.py` vía `@vercel/python`, ver `vercel.json`)
  con `DATABASE_URL` (Supabase) y `SECRET_KEY` como env vars.
  Tras el primer deploy: `POST /api/seed` para sembrar datos.
- **UI** → Streamlit Community Cloud, Railway, Render o Fly.io
  (cualquier host que corra el `Dockerfile.ui`), con `CENIT_API_URL`
  apuntando a la API.

## Vistas

- **Mi día** — tus tareas agrupadas: vencidas, para hoy, próximas, en curso.
- **Kanban** — 4 columnas por estado, mover tareas entre estados.
- **Eisenhower** — matriz 2×2 importante/urgente (excluye completadas).
- **Riesgos** — top 30 por `risk_score` (probabilidad × impacto × (1 − cobertura)).
- **Analytics** — métricas, throughput mensual, lead time por persona.
- **Equipo** — carga por responsable; los admins crean usuarios.
