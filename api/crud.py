from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Optional
from . import models, schemas
from .auth import hash_password
import random

# ── Users ──────────────────────────────────────────────────────────────────────

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_all_users(db: Session):
    return db.query(models.User).all()

def create_user(db: Session, data: schemas.UserCreate):
    user = models.User(
        username=data.username,
        name=data.name,
        hashed_password=hash_password(data.password),
        role=data.role,
        color=data.color,
    )
    db.add(user); db.commit(); db.refresh(user)
    return user

# ── Tasks ──────────────────────────────────────────────────────────────────────

def get_tasks(db: Session, status=None, responsable=None, prioridad=None, entidad=None):
    q = db.query(models.Task)
    if status:      q = q.filter(models.Task.estado == status)
    if responsable: q = q.filter(models.Task.responsable == responsable)
    if prioridad:   q = q.filter(models.Task.prioridad == prioridad)
    if entidad:     q = q.filter(models.Task.entidad == entidad)
    tasks = q.order_by(models.Task.created_at.desc()).all()
    for t in tasks:
        t.lead_time_days  # computed property access
    return tasks

def create_task(db: Session, data: schemas.TaskCreate, created_by: str):
    task = models.Task(**data.model_dump(), created_by=created_by)
    if data.estado == "En Proceso" and not data.fecha_inicio:
        task.fecha_inicio = datetime.utcnow()
    db.add(task); db.commit(); db.refresh(task)
    return task

def update_task(db: Session, task_id: int, data: schemas.TaskUpdate):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task: return None
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    for k, v in update_data.items():
        setattr(task, k, v)
    if data.estado == "Completado" and not task.fecha_completado:
        task.fecha_completado = datetime.utcnow()
        if not task.fecha_inicio:
            task.fecha_inicio = task.created_at
    db.commit(); db.refresh(task)
    return task

def patch_task_status(db: Session, task_id: int, estado: str):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task: return None
    task.estado = estado
    if estado == "En Proceso" and not task.fecha_inicio:
        task.fecha_inicio = datetime.utcnow()
    if estado == "Completado" and not task.fecha_completado:
        task.fecha_completado = datetime.utcnow()
        if not task.fecha_inicio:
            task.fecha_inicio = task.created_at
    db.commit(); db.refresh(task)
    return task

def delete_task(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task: return False
    db.delete(task); db.commit()
    return True

# ── Analytics ─────────────────────────────────────────────────────────────────

def get_summary(db: Session):
    all_tasks = db.query(models.Task).all()
    total      = len(all_tasks)
    by_estado  = {}
    by_prio    = {}
    by_entidad = {}
    urgentes   = 0
    completadas_con_lt = [t for t in all_tasks if t.estado == "Completado" and t.lead_time_days is not None]
    avg_lt     = round(sum(t.lead_time_days for t in completadas_con_lt) / len(completadas_con_lt), 1) if completadas_con_lt else 0
    vencidas   = 0
    today      = datetime.utcnow()
    for t in all_tasks:
        by_estado[t.estado]   = by_estado.get(t.estado, 0) + 1
        by_prio[t.prioridad]  = by_prio.get(t.prioridad, 0) + 1
        by_entidad[t.entidad] = by_entidad.get(t.entidad, 0) + 1
        if t.prioridad == "Urgente": urgentes += 1
        if t.fecha_fin and t.fecha_fin < today and t.estado not in ("Completado",):
            vencidas += 1
    return {
        "total": total,
        "urgentes": urgentes,
        "avg_lead_time": avg_lt,
        "vencidas": vencidas,
        "completadas": by_estado.get("Completado", 0),
        "en_proceso": by_estado.get("En Proceso", 0),
        "no_iniciado": by_estado.get("No Iniciado", 0),
        "pausado": by_estado.get("Pausado", 0),
        "by_estado": by_estado,
        "by_prioridad": by_prio,
        "by_entidad": by_entidad,
    }

def get_throughput(db: Session):
    tasks = db.query(models.Task).filter(
        models.Task.estado == "Completado",
        models.Task.fecha_completado.isnot(None)
    ).all()
    monthly = {}
    for t in tasks:
        key = t.fecha_completado.strftime("%Y-%m")
        monthly[key] = monthly.get(key, 0) + 1
    return [{"mes": k, "completadas": v} for k, v in sorted(monthly.items())]

def get_lead_time_by_person(db: Session):
    tasks = [t for t in db.query(models.Task).filter(models.Task.estado == "Completado").all()
             if t.lead_time_days is not None and t.responsable]
    by_person = {}
    for t in tasks:
        p = t.responsable
        if p not in by_person: by_person[p] = []
        by_person[p].append(t.lead_time_days)
    result = []
    for p, lts in by_person.items():
        result.append({
            "responsable": p,
            "count": len(lts),
            "avg": round(sum(lts)/len(lts), 1),
            "min": round(min(lts), 1),
            "max": round(max(lts), 1),
        })
    return sorted(result, key=lambda x: -x["count"])

# ── Seed ──────────────────────────────────────────────────────────────────────

def seed_initial_data(db: Session):
    team = [
        ("fidel",    "Fidel",         "fidel123",   "admin", "#1B2A4A"),
        ("lorena",   "Lorena",        "lorena123",  "member","#0F766E"),
        ("jimmy",    "Jimmy",         "jimmy123",   "member","#7C3AED"),
        ("jhezir",   "Jhezir",        "jhezir123",  "member","#2563EB"),
        ("harold",   "Harold",        "harold123",  "member","#16A34A"),
        ("felipe",   "Felipe Arenas", "felipe123",  "member","#D97706"),
        ("luispe",   "Luis Peña",     "luispe123",  "member","#F97316"),
        ("luispl",   "Luis Pelaez",   "luispl123",  "member","#DB2777"),
        ("luisr",    "Luis Rosas",    "luisr123",   "member","#6B7280"),
        ("danny",    "Danny",         "danny123",   "member","#0EA5E9"),
        ("moshe",    "Moshe",         "Moshe21",    "member","#84CC16"),
    ]
    for username, name, pwd, role, color in team:
        u = models.User(username=username, name=name, hashed_password=hash_password(pwd), role=role, color=color)
        db.add(u)

    now = datetime.utcnow()
    sample_tasks = [
        ("Xertify","Desarrollo","Javeriana Educacion continua","Ajustar módulo configuración plantilla email blockchain","Urgente","No Iniciado","Jhezir",now-timedelta(days=3),now+timedelta(days=2)),
        ("Xertify","Soporte","Javeriana","Certificados SIPEC no llegaban completos — seguimiento","Urgente","En Proceso","Lorena",now-timedelta(days=5),None),
        ("Xertify","Soporte","Javeriana","Cada 20 min no salen los certificados","Urgente","No Iniciado","Lorena",now-timedelta(days=5),None),
        ("Xertify","Marketing","Interno","Videos demostrativos x2 (Generador y Verificador) Web","Urgente","En Proceso","Luis Peña",now-timedelta(days=15),now+timedelta(days=11)),
        ("Xertify","Operaciones","BrightSpace","Dar respuesta credenciales — análisis integración API","Alta","En Proceso","Jhezir",now-timedelta(days=12),now+timedelta(days=18)),
        ("Xertify","Wallet","Interno","Wallet versión Mobile/Responsive","Alta","En Proceso","Luis Peña",now-timedelta(days=8),now+timedelta(days=2)),
        ("Xertify","Operaciones","UniAndes","Integración de insignias","Alta","En Proceso","Felipe Arenas",now-timedelta(days=6),now+timedelta(days=4)),
        ("Xertify","Operaciones","U Sabana","Piloto — Seguimiento","Alta","En Proceso","Felipe Arenas",now-timedelta(days=6),now+timedelta(days=9)),
        ("Xertiflow","Operaciones","EIA Firmas","Firmas Electrónicas — Colocación grupo A","Alta","En Proceso","Lorena",now-timedelta(days=3),now+timedelta(days=7)),
        ("Xertify","Generador","Javeriana","Canva Email en plantillas HTML","Alta","En Proceso","Jhezir",now-timedelta(days=4),now+timedelta(days=15)),
        ("Xertify","Operaciones","Interno","Migración Bucket S3 — Xertify/XertiCloud","Alta","En Proceso","Fidel",now-timedelta(days=10),now+timedelta(days=4)),
        ("Xertify","Generador","Interno","Mejoras de comunidades","Alta","En Proceso","Jimmy",now-timedelta(days=3),now+timedelta(days=3)),
        ("Xertify","Marketing","Interno","Montar Página Quienes Somos (Replit)","Alta","En Proceso","Luis Peña",now-timedelta(days=7),None),
        ("Xertify","Marketing","Interno","Montar Página Aliados Estratégicos (Replit)","Alta","En Proceso","Luis Peña",now-timedelta(days=7),None),
        ("Xertify","Marketing","Interno","Montar Página Integraciones API (Replit)","Alta","En Proceso","Luis Peña",now-timedelta(days=7),None),
        ("Xertiflow","Operaciones","Interno","Implementar Fastrack en Xertiflow","Alta","No Iniciado","Luis Pelaez",now-timedelta(days=10),now+timedelta(days=2)),
        ("Xertify","Generador","Interno","Realizar nueva propuesta Programas (Power)","Alta","En Proceso","Luis Peña",now-timedelta(days=4),now+timedelta(days=9)),
        ("Xertify","Generador","Interno","Estadísticas métricas de redes sociales","Alta","No Iniciado","Jimmy",None,None),
        ("Xertify","Generador","Interno","Carga masiva XLS/CSV/API para cursos","Alta","No Iniciado","Jimmy",None,None),
        ("Xertify","Wallet","Interno","Configuración encuesta antes de ver diploma","Alta","No Iniciado","Jimmy",None,None),
        ("Xertiflow","Operaciones","Interno","Ambiente de Pruebas CMV","Media","No Iniciado","Danny",now,now+timedelta(days=5)),
        ("Xertify","Operaciones","Interno","Multilenguaje OB 3.0","Media","Pausado","Jhezir",now-timedelta(days=11),None),
        ("Xertiflow","Operaciones","Interno","Bug Visual Bloque HTML Imágenes y firmas","Media","Pausado","Lorena",now-timedelta(days=14),None),
        ("Xertiflow","Operaciones","Ibero","Crear proceso de Contratos","Media","Pausado","Lorena",now-timedelta(days=13),None),
        ("Xertify","Soporte","Interno","Inducción a Moshe","Media","En Proceso","Luis Rosas",now-timedelta(days=9),now+timedelta(days=7)),
        ("Xertiflow","Operaciones","Interno","Socket Engine N8N","Baja","Pausado","Fidel",now-timedelta(days=20),None),
        ("Xertiflow","Operaciones","Interno","Engine flujo N8N (Sincrono/Asíncrono)","Baja","Pausado","Fidel",now-timedelta(days=16),None),
        ("Xertify","Soporte","EAFIT","Falla en front por timeout — Cloudflare","Baja","No Iniciado","Fidel",now-timedelta(days=2),now+timedelta(days=8)),
    ]
    for ent,proy,cli,desc,prio,est,resp,fi,ff in sample_tasks:
        t = models.Task(entidad=ent,proyecto=proy,cliente=cli,descripcion=desc,
                        prioridad=prio,estado=est,responsable=resp,
                        fecha_inicio=fi,fecha_fin=ff,created_by="fidel")
        db.add(t)

    # Some completed tasks with real lead times
    completed = [
        ("Xertify","Generador","Interno","Ajustar print","Alta","Completado","Jimmy",now-timedelta(days=4),now-timedelta(days=3)),
        ("Xertify","Generador","scare","Crear 3 plantillas Simposio Seguridad 2026","Media","Completado","Moshe",now-timedelta(days=4),now-timedelta(days=4)),
        ("Xertify","Operaciones","UniAndes","Organización plantilla logo y firma","Media","Completado","Moshe",now-timedelta(days=5),now-timedelta(days=4)),
        ("Xertify","Operaciones","Conmeva","Validar cursos","Media","Completado","Jimmy",now-timedelta(days=14),now-timedelta(days=10)),
        ("Xertiflow","Desarrollo","Constructora","Permitir copiar y pegar instrucciones","Alta","Completado","Luis Pelaez",now-timedelta(days=30),now-timedelta(days=1)),
        ("Xertify","Operaciones","Externado","Acta general","Urgente","Completado","Jimmy",now-timedelta(days=35),now-timedelta(days=23)),
    ]
    for ent,proy,cli,desc,prio,est,resp,fi,fc in completed:
        t = models.Task(entidad=ent,proyecto=proy,cliente=cli,descripcion=desc,
                        prioridad=prio,estado=est,responsable=resp,
                        fecha_inicio=fi,fecha_fin=fi+timedelta(days=1),
                        fecha_completado=fc,created_by="fidel")
        db.add(t)

    db.commit()
