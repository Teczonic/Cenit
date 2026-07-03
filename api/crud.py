from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Optional
from . import models, schemas
from .auth import hash_password
from domain.services import FlowService
import random


def _log_transition(db: Session, task_id: int, from_state, to_state: str,
                    changed_by: Optional[str] = None, changed_at: Optional[datetime] = None):
    """Registra un cambio de estado. No hace commit — se une a la transacción del caller."""
    db.add(models.TaskStateTransition(
        task_id=task_id, from_state=from_state, to_state=to_state,
        changed_by=changed_by, changed_at=changed_at or datetime.utcnow(),
    ))

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
    _log_transition(db, task.id, None, task.estado, changed_by=created_by)
    db.commit()
    return task

def update_task(db: Session, task_id: int, data: schemas.TaskUpdate, changed_by: Optional[str] = None):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task: return None
    old_estado = task.estado
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    for k, v in update_data.items():
        setattr(task, k, v)
    if data.estado == "Completado" and not task.fecha_completado:
        task.fecha_completado = datetime.utcnow()
        if not task.fecha_inicio:
            task.fecha_inicio = task.created_at
    if data.estado and data.estado != old_estado:
        _log_transition(db, task.id, old_estado, data.estado, changed_by=changed_by)
    db.commit(); db.refresh(task)
    return task

def patch_task_status(db: Session, task_id: int, estado: str, changed_by: Optional[str] = None):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task: return None
    old_estado = task.estado
    task.estado = estado
    if estado == "En Proceso" and not task.fecha_inicio:
        task.fecha_inicio = datetime.utcnow()
    if estado == "Completado" and not task.fecha_completado:
        task.fecha_completado = datetime.utcnow()
        if not task.fecha_inicio:
            task.fecha_inicio = task.created_at
    if estado != old_estado:
        _log_transition(db, task.id, old_estado, estado, changed_by=changed_by)
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

# ── Flujo (task_state_transitions) ──────────────────────────────────────────────

def get_transitions(db: Session, task_id: int):
    return (db.query(models.TaskStateTransition)
              .filter(models.TaskStateTransition.task_id == task_id)
              .order_by(models.TaskStateTransition.changed_at)
              .all())

def get_flow_metrics(db: Session):
    """Lead time real, cycle time, flow efficiency y aging derivados del historial."""
    rows = db.query(models.TaskStateTransition).all()

    def _naive(dt):
        # Postgres devuelve tz-aware; el dominio compara contra un 'ahora' naive.
        return dt.replace(tzinfo=None) if dt and dt.tzinfo else dt

    transiciones = [
        {"task_id": r.task_id, "from_state": r.from_state,
         "to_state": r.to_state, "changed_at": _naive(r.changed_at)}
        for r in rows
    ]
    return FlowService().resumen(transiciones, datetime.utcnow())


# ── OKRs (dirección) ────────────────────────────────────────────────────────

def _kr_dict(kr, svc) -> dict:
    d = {
        "id": kr.id, "objective_id": kr.objective_id, "titulo": kr.titulo,
        "valor_inicial": kr.valor_inicial, "valor_meta": kr.valor_meta,
        "valor_actual": kr.valor_actual, "unidad": kr.unidad,
    }
    d["progreso"] = svc.progreso_kr(d)
    return d

def create_okr_cycle(db: Session, data: schemas.OkrCycleCreate):
    cycle = models.OkrCycle(nombre=data.nombre, fecha_inicio=data.fecha_inicio,
                            fecha_fin=data.fecha_fin)
    db.add(cycle); db.commit(); db.refresh(cycle)
    return {"id": cycle.id, "nombre": cycle.nombre, "fecha_inicio": cycle.fecha_inicio,
            "fecha_fin": cycle.fecha_fin, "estado": cycle.estado}

def list_okr_cycles(db: Session):
    return [{"id": c.id, "nombre": c.nombre, "fecha_inicio": c.fecha_inicio,
             "fecha_fin": c.fecha_fin, "estado": c.estado}
            for c in db.query(models.OkrCycle).order_by(models.OkrCycle.fecha_inicio.desc()).all()]

def create_objective(db: Session, data: schemas.ObjectiveCreate):
    obj = models.Objective(cycle_id=data.cycle_id, titulo=data.titulo,
                           owner=data.owner, entidad=data.entidad)
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "cycle_id": obj.cycle_id, "titulo": obj.titulo,
            "owner": obj.owner, "entidad": obj.entidad}

def create_key_result(db: Session, data: schemas.KeyResultCreate):
    kr = models.KeyResult(objective_id=data.objective_id, titulo=data.titulo,
                          valor_inicial=data.valor_inicial, valor_meta=data.valor_meta,
                          valor_actual=data.valor_actual, unidad=data.unidad)
    db.add(kr); db.commit(); db.refresh(kr)
    from domain.okrs import OkrService
    return _kr_dict(kr, OkrService())

def patch_kr_valor(db: Session, kr_id: int, valor_actual: float):
    kr = db.query(models.KeyResult).filter(models.KeyResult.id == kr_id).first()
    if not kr:
        return None
    kr.valor_actual = valor_actual
    db.commit(); db.refresh(kr)
    from domain.okrs import OkrService
    return _kr_dict(kr, OkrService())

def link_task_kr(db: Session, task_id: int, kr_id: int):
    exists = db.query(models.TaskKeyResult).filter_by(task_id=task_id, kr_id=kr_id).first()
    if not exists:
        db.add(models.TaskKeyResult(task_id=task_id, kr_id=kr_id)); db.commit()
    return {"task_id": task_id, "kr_id": kr_id}

def get_okr_overview(db: Session, cycle_id: Optional[int] = None):
    from domain.okrs import OkrService
    svc = OkrService()
    q = db.query(models.Objective)
    if cycle_id:
        q = q.filter(models.Objective.cycle_id == cycle_id)
    objectives = []
    for o in q.all():
        krs = [_kr_dict(k, svc) for k in
               db.query(models.KeyResult).filter(models.KeyResult.objective_id == o.id).all()]
        objectives.append({
            "id": o.id, "cycle_id": o.cycle_id, "titulo": o.titulo,
            "owner": o.owner, "entidad": o.entidad,
            "progreso": svc.progreso_objective(krs), "key_results": krs,
        })
    tareas = [{"id": t.id, "estado": t.estado} for t in db.query(models.Task).all()]
    vinculadas = {l.task_id for l in db.query(models.TaskKeyResult).all()}
    return {
        "objectives": objectives,
        "alignment_ratio": svc.alignment_ratio(tareas, vinculadas),
    }


# ── Seed ──────────────────────────────────────────────────────────────────────

def _backfill_transitions(db: Session, task: "models.Task"):
    """Reconstruye un historial plausible para una tarea sembrada, así el
    cockpit y /api/analytics/flow muestran datos históricos en las demos."""
    created = task.fecha_inicio or task.created_at or datetime.utcnow()
    _log_transition(db, task.id, None, "No Iniciado", changed_by="fidel", changed_at=created)
    if task.fecha_inicio and task.estado in ("En Proceso", "Pausado", "Completado"):
        _log_transition(db, task.id, "No Iniciado", "En Proceso",
                        changed_by="fidel", changed_at=task.fecha_inicio)
    if task.estado == "Pausado":
        _log_transition(db, task.id, "En Proceso", "Pausado",
                        changed_by="fidel", changed_at=task.fecha_inicio or created)
    if task.fecha_completado:
        _log_transition(db, task.id, "En Proceso", "Completado",
                        changed_by="fidel", changed_at=task.fecha_completado)


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

    # Historial de transiciones para que el cockpit muestre datos desde el arranque
    for t in db.query(models.Task).all():
        _backfill_transitions(db, t)
    db.commit()

    # OKRs de ejemplo (capa de dirección) para que la vista no arranque vacía
    cycle = models.OkrCycle(nombre="Q3 2026", fecha_inicio=now.date(),
                            fecha_fin=(now + timedelta(days=90)).date(), estado="activo")
    db.add(cycle); db.commit(); db.refresh(cycle)

    obj1 = models.Objective(cycle_id=cycle.id, entidad="Xertify", owner="Fidel",
                            titulo="Acelerar la entrega a clientes sin perder calidad")
    obj2 = models.Objective(cycle_id=cycle.id, entidad="Xertiflow", owner="Lorena",
                            titulo="Estabilizar la operación del equipo")
    db.add_all([obj1, obj2]); db.commit(); db.refresh(obj1); db.refresh(obj2)

    krs = [
        models.KeyResult(objective_id=obj1.id, titulo="Lead time promedio bajo 5 días",
                         valor_inicial=8, valor_meta=5, valor_actual=7, unidad="días"),
        models.KeyResult(objective_id=obj1.id, titulo="Tareas vencidas en cero",
                         valor_inicial=5, valor_meta=0, valor_actual=2, unidad="tareas"),
        models.KeyResult(objective_id=obj2.id, titulo="Flow efficiency por encima de 85%",
                         valor_inicial=70, valor_meta=85, valor_actual=80, unidad="%"),
    ]
    db.add_all(krs); db.commit()
    for kr in krs:
        db.refresh(kr)

    # Vincular algunas tareas abiertas a los KRs (base del alignment ratio)
    abiertas = db.query(models.Task).filter(models.Task.estado != "Completado").limit(6).all()
    for i, t in enumerate(abiertas):
        db.add(models.TaskKeyResult(task_id=t.id, kr_id=krs[i % len(krs)].id))
    db.commit()
