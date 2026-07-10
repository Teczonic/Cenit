from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status, Request # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import os

from .database import engine, get_db, Base
from . import models, schemas, crud
from .auth import create_access_token, verify_token, hash_password, verify_password

def _ensure_schema_upgrades():
    """Columnas nuevas sobre tablas existentes — create_all no altera tablas,
    así que las bases ya desplegadas (SQLite dev / Supabase prod) se parchan aquí."""
    upgrades = {"tasks": {"story_points": "INTEGER"}}
    insp = inspect(engine)
    for tabla, columnas in upgrades.items():
        if tabla not in insp.get_table_names():
            continue
        existentes = {c["name"] for c in insp.get_columns(tabla)}
        for col, tipo in columnas.items():
            if col not in existentes:
                with engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {col} {tipo}"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        _ensure_schema_upgrades()
        db = next(get_db())
        try:
            if not crud.get_all_users(db):
                crud.seed_initial_data(db)
        finally:
            db.close()
    except Exception as e:
        print(f"[lifespan] DB init error (app will still start): {e}")
    yield

app = FastAPI(title="Cenit API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth ──────────────────────────────────────────────────────────────────────────────

@app.post("/api/auth/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    try:
        user = crud.get_user_by_username(db, data.username)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error de base de datos: {e}")
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})
    return {"token": token, "user": {"id": user.id, "username": user.username, "name": user.name, "role": user.role, "color": user.color}}

@app.get("/api/auth/me")
def me(request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    user = crud.get_user(db, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": user.id, "username": user.username, "name": user.name, "role": user.role, "color": user.color}

# ── Users ──────────────────────────────────────────────────────────────────────────

@app.get("/api/users", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return crud.get_all_users(db)

@app.post("/api/users", response_model=schemas.UserOut)
def create_user(data: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden crear usuarios")
    existing = crud.get_user_by_username(db, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return crud.create_user(db, data)

# ── Tasks ──────────────────────────────────────────────────────────────────────────

@app.get("/api/tasks", response_model=List[schemas.TaskOut])
def list_tasks(
    status: Optional[str] = None,
    responsable: Optional[str] = None,
    prioridad: Optional[str] = None,
    entidad: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_tasks(db, status=status, responsable=responsable, prioridad=prioridad, entidad=entidad)

@app.post("/api/tasks", response_model=schemas.TaskOut)
def create_task(data: schemas.TaskCreate, request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    _validar_story_points(data.story_points)
    return crud.create_task(db, data, created_by=payload["username"])

@app.put("/api/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    _validar_story_points(data.story_points)
    task = crud.update_task(db, task_id, data, changed_by=payload.get("username"))
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden eliminar tareas")
    ok = crud.delete_task(db, task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"ok": True}

@app.patch("/api/tasks/{task_id}/status")
def patch_status(task_id: int, body: schemas.StatusPatch, request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    # Límite WIP: Cenit persuade, no bloquea — 409 con contexto; force=true registra la excepción
    if body.estado != task.estado and not body.force:
        veredicto = crud.evaluar_wip_movimiento(db, body.estado, responsable=task.responsable)
        if veredicto["excedido"]:
            raise HTTPException(status_code=409, detail={
                "mensaje": f'Límite WIP de «{body.estado}» alcanzado '
                           f'({veredicto["wip_actual"]}/{veredicto["wip_limit"]}).',
                "sugerencia": "Completa o pausa una tarea antes de iniciar otra, "
                              "o mueve de todas formas para registrar la excepción.",
                **veredicto,
            })

    task = crud.patch_task_status(db, task_id, body.estado, changed_by=payload.get("username"))
    return task

@app.get("/api/tasks/{task_id}/transitions", response_model=List[schemas.TransitionOut])
def task_transitions(task_id: int, db: Session = Depends(get_db)):
    return crud.get_transitions(db, task_id)

# ── Kanban: límites WIP y políticas ───────────────────────────────────────────────────

@app.get("/api/kanban/columns", response_model=List[schemas.KanbanColumnOut])
def kanban_columns(db: Session = Depends(get_db)):
    return crud.get_kanban_columns(db)

@app.put("/api/kanban/columns/{estado}", response_model=schemas.KanbanColumnOut)
def update_kanban_column(estado: str, data: schemas.KanbanColumnUpdate,
                         request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden editar los límites del tablero")
    if data.wip_limit_scope and data.wip_limit_scope not in ("board", "person"):
        raise HTTPException(status_code=400, detail="wip_limit_scope debe ser board o person")
    col = crud.update_kanban_column(db, estado, data)
    if not col:
        raise HTTPException(status_code=404, detail="Columna no encontrada")
    return col

@app.get("/api/kanban/wip-status")
def kanban_wip_status(db: Session = Depends(get_db)):
    """Ocupación actual de cada columna contra su límite WIP."""
    return crud.get_wip_status(db)

# ── Analytics ─────────────────────────────────────────────────────────────────────────

@app.get("/api/analytics/summary")
def analytics_summary(db: Session = Depends(get_db)):
    return crud.get_summary(db)

@app.get("/api/analytics/throughput")
def analytics_throughput(db: Session = Depends(get_db)):
    return crud.get_throughput(db)

@app.get("/api/analytics/lead_time")
def analytics_lead_time(db: Session = Depends(get_db)):
    return crud.get_lead_time_by_person(db)

@app.get("/api/analytics/flow")
def analytics_flow(db: Session = Depends(get_db)):
    """Motor de flujo: lead time real, cycle time, flow efficiency y aging."""
    return crud.get_flow_metrics(db)

# ── Sprints ligeros (Linear Cycles) ─────────────────────────────────────────

FIBONACCI = (1, 2, 3, 5, 8, 13, 21)

def _validar_story_points(points):
    if points is not None and points not in FIBONACCI:
        raise HTTPException(status_code=400,
                            detail=f"story_points debe ser Fibonacci: {FIBONACCI}")

@app.post("/api/sprints")
def create_sprint(data: schemas.SprintCreate, request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    if data.fecha_fin <= data.fecha_inicio:
        raise HTTPException(status_code=400, detail="fecha_fin debe ser posterior a fecha_inicio")
    sprint = crud.create_sprint(db, data, created_by=payload["username"])
    if sprint is None:
        raise HTTPException(status_code=400, detail="Ya existe un sprint con ese nombre en la entidad")
    return sprint

@app.get("/api/sprints")
def list_sprints(entidad: Optional[str] = None, estado: Optional[str] = None,
                 db: Session = Depends(get_db)):
    return crud.list_sprints(db, entidad=entidad, estado=estado)

@app.get("/api/sprints/{sprint_id}")
def sprint_detail(sprint_id: int, db: Session = Depends(get_db)):
    detalle = crud.get_sprint_detail(db, sprint_id)
    if not detalle:
        raise HTTPException(status_code=404, detail="Sprint no encontrado")
    return detalle

@app.patch("/api/sprints/{sprint_id}")
def patch_sprint(sprint_id: int, data: schemas.SprintPatch, request: Request,
                 db: Session = Depends(get_db)):
    verify_token(request)
    if data.estado and data.estado not in ("planificado", "activo", "cerrado", "cancelado"):
        raise HTTPException(status_code=400, detail="Estado de sprint inválido")
    res = crud.patch_sprint(db, sprint_id, data)
    if res is None:
        raise HTTPException(status_code=404, detail="Sprint no encontrado")
    if "error" in res:
        raise HTTPException(status_code=409, detail=res["error"])
    return res

@app.post("/api/sprints/{sprint_id}/tasks")
def add_sprint_tasks(sprint_id: int, body: schemas.SprintTasksAdd, request: Request,
                     db: Session = Depends(get_db)):
    verify_token(request)
    res = crud.add_sprint_tasks(db, sprint_id, body.task_ids)
    if res is None:
        raise HTTPException(status_code=404, detail="Sprint no encontrado")
    if not res["ok"]:
        # Compromiso sin estimación no es compromiso — 400 con las tareas sin puntos
        raise HTTPException(status_code=400, detail={
            "mensaje": res["warning"], "sin_puntos": res["sin_puntos"]})
    return res

@app.delete("/api/sprints/{sprint_id}/tasks/{task_id}")
def remove_sprint_task(sprint_id: int, task_id: int, request: Request,
                       db: Session = Depends(get_db)):
    verify_token(request)
    if not crud.remove_sprint_task(db, sprint_id, task_id):
        raise HTTPException(status_code=404, detail="La tarea no está en el sprint")
    return {"ok": True}

@app.post("/api/sprints/{sprint_id}/close")
def close_sprint(sprint_id: int, request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
    sprint = crud.get_sprint_model(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint no encontrado")
    if payload.get("role") != "admin" and payload.get("username") != sprint.created_by:
        raise HTTPException(status_code=403, detail="Solo el creador del sprint o un admin puede cerrarlo")
    if sprint.estado == "cerrado":
        raise HTTPException(status_code=400, detail="El sprint ya está cerrado")
    return crud.close_sprint(db, sprint_id)

@app.get("/api/sprints/{sprint_id}/burndown")
def sprint_burndown(sprint_id: int, db: Session = Depends(get_db)):
    res = crud.get_burndown(db, sprint_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Sprint no encontrado")
    return res

@app.get("/api/analytics/velocity")
def analytics_velocity(entidad: Optional[str] = None, n: int = 6, db: Session = Depends(get_db)):
    """Histórico de velocity y Say/Do — la predictibilidad del equipo."""
    return crud.get_velocity_history(db, entidad=entidad, n=n)

# ── OKRs (dirección) ────────────────────────────────────────────────────────

@app.get("/api/okr/cycles")
def okr_cycles(db: Session = Depends(get_db)):
    return crud.list_okr_cycles(db)

@app.post("/api/okr/cycles")
def create_okr_cycle(data: schemas.OkrCycleCreate, request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    return crud.create_okr_cycle(db, data)

@app.get("/api/okr/overview")
def okr_overview(cycle_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_okr_overview(db, cycle_id=cycle_id)

@app.post("/api/okr/objectives")
def create_objective(data: schemas.ObjectiveCreate, request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    return crud.create_objective(db, data)

@app.post("/api/okr/key-results")
def create_key_result(data: schemas.KeyResultCreate, request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    return crud.create_key_result(db, data)

@app.patch("/api/okr/key-results/{kr_id}")
def patch_kr(kr_id: int, body: schemas.KRValorPatch, request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    kr = crud.patch_kr_valor(db, kr_id, body.valor_actual)
    if not kr:
        raise HTTPException(status_code=404, detail="Key result no encontrado")
    return kr

@app.post("/api/tasks/{task_id}/key-results/{kr_id}")
def link_task_kr(task_id: int, kr_id: int, request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    return crud.link_task_kr(db, task_id, kr_id)

# ── KPIs / Motor de métricas ──────────────────────────────────────────────────

@app.get("/api/kpis/overview")
def kpi_overview(entidad: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_kpi_overview(db, entidad=entidad)

@app.post("/api/kpis")
def create_kpi(data: schemas.MetricDefinitionCreate, request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    if data.direccion not in ("up", "down", "band"):
        raise HTTPException(status_code=400, detail="dirección debe ser up, down o band")
    return crud.create_metric_definition(db, data)

@app.post("/api/kpis/{metric_id}/measurements")
def add_measurement(metric_id: int, data: schemas.MeasurementCreate, request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    res = crud.record_measurement(db, metric_id, data)
    if not res:
        raise HTTPException(status_code=404, detail="KPI no encontrado")
    return res

# ── Seed ──────────────────────────────────────────────────────────────────────────────

@app.post("/api/seed")
def seed_db(db: Session = Depends(get_db)):
    """Seed initial data — run once after deploy"""
    if crud.get_all_users(db):
        return {"message": "Ya tiene datos"}
    crud.seed_initial_data(db)
    return {"message": "Datos iniciales creados correctamente"}

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    """Chequeo de salud para monitoreo del piloto: ¿la API responde y la DB está arriba?"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "up"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "degraded", "db": str(e)})

@app.get("/")
def root():
    return {
        "status": "Cenit API running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
