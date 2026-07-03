from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status, Request # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import os

from .database import engine, get_db, Base
from . import models, schemas, crud
from .auth import create_access_token, verify_token, hash_password, verify_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
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
    return crud.create_task(db, data, created_by=payload["username"])

@app.put("/api/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate, request: Request, db: Session = Depends(get_db)):
    payload = verify_token(request)
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
    task = crud.patch_task_status(db, task_id, body.estado, changed_by=payload.get("username"))
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.get("/api/tasks/{task_id}/transitions", response_model=List[schemas.TransitionOut])
def task_transitions(task_id: int, db: Session = Depends(get_db)):
    return crud.get_transitions(db, task_id)

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
