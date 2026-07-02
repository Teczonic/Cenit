"""
Importa base_datos_excel.csv a la base de datos SQLite de Cenit.
Ejecutar desde la carpeta cenit/:
    python import_csv.py
"""
import csv
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from api.database import SessionLocal, engine, Base
from api import models
from api.auth import hash_password

Base.metadata.create_all(bind=engine)

CSV_PATH = r"C:\Users\daiss\Documents\Moshe_Xertify\Moshe Company\ideas\files\base_datos_excel.csv"

VALID_PRIORIDADES = {"Urgente", "Alta", "Media", "Baja"}
VALID_ESTADOS     = {"No Iniciado", "En Proceso", "Pausado", "Completado"}

TEAM = [
    ("fidel",    "Fidel",         "fidel123",   "admin",  "#1B2A4A"),
    ("lorena",   "Lorena",        "lorena123",  "member", "#0F766E"),
    ("jimmy",    "Jimmy",         "jimmy123",   "admin",  "#7C3AED"),
    ("jhezir",   "Jhezir",        "jhezir123",  "member", "#2563EB"),
    ("harold",   "Harold",        "harold123",  "member", "#16A34A"),
    ("felipe",   "Felipe Arenas", "felipe123",  "admin",  "#D97706"),
    ("luispe",   "Luis Peña",     "luispe123",  "member", "#6B7280"),
    ("luispl",   "Luis Pelaez",   "luispl123",  "admin",  "#DB2777"),
    ("luisr",    "Luis Rosas",    "luisr123",   "member", "#84CC16"),
    ("danny",    "Danny",         "danny123",   "admin",  "#0EA5E9"),
    ("moshe",    "Moshe",         "moshe123",   "admin",  "#F97316"),
]


def parse_date(s: str):
    if not s:
        return None
    s = s.strip()
    if s.lower() in ("pendiente", ""):
        return None
    # Fix typos like year 0202 or 0206
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            d = datetime.strptime(s, fmt)
            if d.year < 2000:
                return None
            return d
        except ValueError:
            pass
    return None


def normalize_prioridad(s: str):
    s = (s or "").strip().capitalize()
    return s if s in VALID_PRIORIDADES else "Media"


def normalize_estado(s: str):
    s = (s or "").strip()
    # case-insensitive match
    for v in VALID_ESTADOS:
        if v.lower() == s.lower():
            return v
    return "No Iniciado"


def normalize_entidad(s: str):
    s = (s or "").strip()
    if "flow" in s.lower():
        return "Xertiflow"
    if "xertify" in s.lower():
        return "Xertify"
    return s or "Xertify"


def main():
    db = SessionLocal()

    # ── Crear usuarios si no existen ─────────────────────────────────────────
    for username, name, pwd, role, color in TEAM:
        if not db.query(models.User).filter(models.User.username == username).first():
            db.add(models.User(
                username=username, name=name,
                hashed_password=hash_password(pwd),
                role=role, color=color,
            ))
    db.commit()
    print("Usuarios OK")

    # ── Importar tareas ───────────────────────────────────────────────────────
    imported = 0
    skipped  = 0

    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header

        for i, row in enumerate(reader, start=2):
            if len(row) < 4:
                skipped += 1
                continue

            # Columnas: Entidad;Proyecto;Cliente;Descripcion;FechaInicio;FechaFin;Prioridad;Estado;Responsable;Comentarios;...
            entidad     = normalize_entidad(row[0] if len(row) > 0 else "")
            proyecto    = (row[1] or "").strip() or None
            cliente     = (row[2] or "").strip() or None
            descripcion = (row[3] or "").strip()
            fecha_ini   = parse_date(row[4] if len(row) > 4 else "")
            fecha_fin   = parse_date(row[5] if len(row) > 5 else "")
            prioridad   = normalize_prioridad(row[6] if len(row) > 6 else "")
            estado      = normalize_estado(row[7] if len(row) > 7 else "")
            responsable = (row[8] if len(row) > 8 else "").strip() or None
            comentarios = (row[9] if len(row) > 9 else "").strip() or None

            if not descripcion:
                skipped += 1
                continue

            # Normalizar responsable "Pendiente" → None
            if responsable and responsable.lower() == "pendiente":
                responsable = None

            fecha_completado = None
            if estado == "Completado" and fecha_fin:
                fecha_completado = fecha_fin

            task = models.Task(
                entidad=entidad,
                proyecto=proyecto,
                cliente=cliente,
                descripcion=descripcion,
                prioridad=prioridad,
                estado=estado,
                responsable=responsable,
                comentarios=comentarios,
                fecha_inicio=fecha_ini,
                fecha_fin=fecha_fin,
                fecha_completado=fecha_completado,
                created_by="import",
            )
            db.add(task)
            imported += 1

    db.commit()
    db.close()
    print(f"Importadas: {imported} tareas | Omitidas: {skipped}")


if __name__ == "__main__":
    main()
