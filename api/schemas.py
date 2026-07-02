from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
