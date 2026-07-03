"""
Run this script ONCE from your local machine to create tables and seed Supabase.

Usage:
    pip install sqlalchemy psycopg2-binary bcrypt
    python seed_supabase.py
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
import bcrypt

# ── Supabase connection ────────────────────────────────────────────────────────
# La URL se lee de la variable de entorno DATABASE_URL — nunca la hardcodees aquí.
#   PowerShell:  $env:DATABASE_URL = "postgresql://usuario:password@host:5432/postgres"
#   bash:        export DATABASE_URL="postgresql://usuario:password@host:5432/postgres"
import os

_url = os.environ.get("DATABASE_URL")
if not _url:
    sys.exit("Falta la variable de entorno DATABASE_URL (connection string de Supabase)")
SUPABASE_URLS = [_url]

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(50), unique=True, index=True, nullable=False)
    name            = Column(String(100), nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role            = Column(String(20), default="member")
    color           = Column(String(7), default="#2563EB")
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

class Task(Base):
    __tablename__ = "tasks"
    id               = Column(Integer, primary_key=True, index=True)
    entidad          = Column(String(50), nullable=False)
    proyecto         = Column(String(80))
    cliente          = Column(String(100))
    descripcion      = Column(Text, nullable=False)
    prioridad        = Column(String(20), default="Media")
    estado           = Column(String(30), default="No Iniciado")
    responsable      = Column(String(80))
    comentarios      = Column(Text)
    fecha_inicio     = Column(DateTime(timezone=True))
    fecha_fin        = Column(DateTime(timezone=True))
    fecha_completado = Column(DateTime(timezone=True))
    created_by       = Column(String(80))
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def seed(engine):
    Session = sessionmaker(bind=engine)
    db = Session()

    if db.query(User).count() > 0:
        print("⚠  Ya hay datos en la base de datos. Saltando seed.")
        db.close()
        return

    now = datetime.utcnow()

    team = [
        ("fidel",  "Fidel",         "fidel123",  "admin",  "#1B2A4A"),
        ("lorena", "Lorena",        "lorena123", "member", "#0F766E"),
        ("jimmy",  "Jimmy",         "jimmy123",  "member", "#7C3AED"),
        ("jhezir", "Jhezir",        "jhezir123", "member", "#2563EB"),
        ("harold", "Harold",        "harold123", "member", "#16A34A"),
        ("felipe", "Felipe Arenas", "felipe123", "member", "#D97706"),
        ("luispe", "Luis Peña",     "luispe123", "member", "#F97316"),
        ("luispl", "Luis Pelaez",   "luispl123", "member", "#DB2777"),
        ("luisr",  "Luis Rosas",    "luisr123",  "member", "#6B7280"),
        ("danny",  "Danny",         "danny123",  "member", "#0EA5E9"),
        ("moshe",  "Moshe",         "Moshe21",   "member", "#84CC16"),
    ]
    for username, name, pwd, role, color in team:
        db.add(User(username=username, name=name,
                    hashed_password=hash_password(pwd), role=role, color=color))
    print(f"✓  {len(team)} usuarios creados")

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
        db.add(Task(entidad=ent, proyecto=proy, cliente=cli, descripcion=desc,
                    prioridad=prio, estado=est, responsable=resp,
                    fecha_inicio=fi, fecha_fin=ff, created_by="fidel"))

    completed = [
        ("Xertify","Generador","Interno","Ajustar print","Alta","Completado","Jimmy",now-timedelta(days=4),now-timedelta(days=3)),
        ("Xertify","Generador","scare","Crear 3 plantillas Simposio Seguridad 2026","Media","Completado","Moshe",now-timedelta(days=4),now-timedelta(days=4)),
        ("Xertify","Operaciones","UniAndes","Organización plantilla logo y firma","Media","Completado","Moshe",now-timedelta(days=5),now-timedelta(days=4)),
        ("Xertify","Operaciones","Conmeva","Validar cursos","Media","Completado","Jimmy",now-timedelta(days=14),now-timedelta(days=10)),
        ("Xertiflow","Desarrollo","Constructora","Permitir copiar y pegar instrucciones","Alta","Completado","Luis Pelaez",now-timedelta(days=30),now-timedelta(days=1)),
        ("Xertify","Operaciones","Externado","Acta general","Urgente","Completado","Jimmy",now-timedelta(days=35),now-timedelta(days=23)),
    ]
    for ent,proy,cli,desc,prio,est,resp,fi,fc in completed:
        db.add(Task(entidad=ent, proyecto=proy, cliente=cli, descripcion=desc,
                    prioridad=prio, estado=est, responsable=resp,
                    fecha_inicio=fi, fecha_fin=fi+timedelta(days=1),
                    fecha_completado=fc, created_by="fidel"))

    print(f"✓  {len(sample_tasks) + len(completed)} tareas creadas")
    db.commit()
    db.close()
    print("✅ Seed completado exitosamente")

def main():
    engine = None
    for url in SUPABASE_URLS:
        try:
            print(f"Probando: {url[:60]}...")
            e = create_engine(url, connect_args={"sslmode": "require"}, pool_pre_ping=True)
            with e.connect() as conn:
                pass
            engine = e
            print(f"✓ Conectado a Supabase")
            break
        except Exception as ex:
            print(f"  ✗ {ex}")

    if engine is None:
        print("\n❌ No se pudo conectar a Supabase.")
        print("Verifica que el usuario y contraseña sean correctos en el Supabase dashboard.")
        sys.exit(1)

    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas")
    seed(engine)

if __name__ == "__main__":
    main()
