from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    name: str
    password: str
    role: str = "member"
    color: str = "#2563EB"

class UserOut(BaseModel):
    id: int
    username: str
    name: str
    role: str
    color: str
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    entidad: str
    proyecto: Optional[str] = None
    cliente: Optional[str] = None
    descripcion: str
    prioridad: str = "Media"
    estado: str = "No Iniciado"
    responsable: Optional[str] = None
    comentarios: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None

class TaskUpdate(BaseModel):
    entidad: Optional[str] = None
    proyecto: Optional[str] = None
    cliente: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    responsable: Optional[str] = None
    comentarios: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None

class StatusPatch(BaseModel):
    estado: str

class TransitionOut(BaseModel):
    id: int
    task_id: int
    from_state: Optional[str]
    to_state: str
    changed_by: Optional[str]
    changed_at: Optional[datetime]
    class Config:
        from_attributes = True

# ── OKRs ────────────────────────────────────────────────────────────────────

class OkrCycleCreate(BaseModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date

class ObjectiveCreate(BaseModel):
    cycle_id: int
    titulo: str
    owner: Optional[str] = None
    entidad: Optional[str] = None

class KeyResultCreate(BaseModel):
    objective_id: int
    titulo: str
    valor_inicial: float = 0
    valor_meta: float
    valor_actual: float = 0
    unidad: Optional[str] = None

class KRValorPatch(BaseModel):
    valor_actual: float

# ── KPIs / Motor de métricas ──────────────────────────────────────────────────

class MetricDefinitionCreate(BaseModel):
    clave: str
    nombre: str
    direccion: str                      # up | down | band
    fuente: str = "manual"
    entidad: Optional[str] = None
    meta: Optional[float] = None
    umbral_alerta: Optional[float] = None
    banda_min: Optional[float] = None
    banda_max: Optional[float] = None
    unidad: Optional[str] = None
    owner: Optional[str] = None

class MeasurementCreate(BaseModel):
    periodo_inicio: date
    periodo_fin: date
    valor: float

class TaskOut(BaseModel):
    id: int
    entidad: str
    proyecto: Optional[str]
    cliente: Optional[str]
    descripcion: str
    prioridad: str
    estado: str
    responsable: Optional[str]
    comentarios: Optional[str]
    fecha_inicio: Optional[datetime]
    fecha_fin: Optional[datetime]
    fecha_completado: Optional[datetime]
    created_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    lead_time_days: Optional[float] = None
    eisenhower: Optional[str] = None
    risk_score: Optional[float] = None
    class Config:
        from_attributes = True
