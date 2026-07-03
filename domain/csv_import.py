"""Parser de CSV puro y testeable — cimiento de la demo diagnóstico (Fase 1.5).

Convierte filas de un CSV exportado de Jira/Trello/Excel en tareas normalizadas
listas para la API de Cenit, sin tocar la base de datos. Detecta las columnas por
alias de encabezado, así un líder puede soltar su export y ver el diagnóstico.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

VALID_PRIORIDADES = {"Urgente", "Alta", "Media", "Baja"}
VALID_ESTADOS = {"No Iniciado", "En Proceso", "Pausado", "Completado"}

# Alias de encabezado → campo canónico de Cenit (todo en minúsculas)
COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "descripcion": ("descripcion", "description", "title", "titulo", "tarea", "task",
                    "summary", "asunto", "name", "nombre", "card name", "item"),
    "estado": ("estado", "status", "state", "columna", "list", "column"),
    "prioridad": ("prioridad", "priority", "importancia"),
    "responsable": ("responsable", "assignee", "owner", "asignado", "assigned to", "members"),
    "entidad": ("entidad", "equipo", "team", "board", "tablero"),
    "proyecto": ("proyecto", "epic", "epica", "sprint", "categoria"),
    "cliente": ("cliente", "client", "customer", "cuenta", "account"),
    "fecha_inicio": ("fecha_inicio", "start", "start date", "inicio", "created", "fecha inicio"),
    "fecha_fin": ("fecha_fin", "due", "due date", "fin", "deadline", "vencimiento", "fecha fin"),
    "comentarios": ("comentarios", "comments", "notes", "notas", "description2"),
}

_DATE_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d",
                 "%d/%m/%y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S")


@dataclass
class ImportResult:
    tasks: list[dict] = field(default_factory=list)
    skipped: int = 0
    warnings: list[str] = field(default_factory=list)
    mapping: dict[str, str] = field(default_factory=dict)  # campo canónico -> encabezado real


def parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    s = str(value).strip()
    if not s or s.lower() in ("pendiente", "none", "null", "-"):
        return None
    for fmt in _DATE_FORMATS:
        try:
            d = datetime.strptime(s, fmt)
            return d if d.year >= 2000 else None
        except ValueError:
            continue
    return None


def normalize_prioridad(value: Optional[str]) -> str:
    s = (value or "").strip().capitalize()
    return s if s in VALID_PRIORIDADES else "Media"


def normalize_estado(value: Optional[str]) -> str:
    s = (value or "").strip().lower()
    for v in VALID_ESTADOS:
        if v.lower() == s:
            return v
    # Sinónimos frecuentes de tableros externos
    if s in ("to do", "todo", "backlog", "open", "nuevo", "por hacer"):
        return "No Iniciado"
    if s in ("in progress", "doing", "wip", "en curso", "en progreso"):
        return "En Proceso"
    if s in ("blocked", "on hold", "bloqueado", "en espera", "paused"):
        return "Pausado"
    if s in ("done", "closed", "resolved", "cerrado", "finalizado", "completed"):
        return "Completado"
    return "No Iniciado"


def normalize_entidad(value: Optional[str]) -> str:
    s = (value or "").strip()
    if "flow" in s.lower():
        return "Xertiflow"
    if "xertify" in s.lower():
        return "Xertify"
    return s or "Xertify"


def detect_mapping(headers: list[str]) -> dict[str, str]:
    """Empareja los encabezados reales del CSV con los campos canónicos de Cenit."""
    lowered = {h.strip().lower(): h for h in headers}
    mapping: dict[str, str] = {}
    for campo, alias in COLUMN_ALIASES.items():
        for a in alias:
            if a in lowered:
                mapping[campo] = lowered[a]
                break
    return mapping


def parse_tasks(rows: list[dict], mapping: Optional[dict[str, str]] = None) -> ImportResult:
    """Normaliza filas (dict encabezado→valor) a tareas listas para la API."""
    result = ImportResult()
    if not rows:
        result.warnings.append("El archivo no tiene filas de datos.")
        return result

    mapping = mapping or detect_mapping(list(rows[0].keys()))
    result.mapping = mapping

    if "descripcion" not in mapping:
        result.warnings.append(
            "No se encontró una columna de descripción/título. "
            "Renombra esa columna o mapéala manualmente."
        )
        result.skipped = len(rows)
        return result

    def val(row: dict, campo: str) -> str:
        col = mapping.get(campo)
        return (str(row.get(col, "")).strip() if col else "")

    for row in rows:
        descripcion = val(row, "descripcion")
        if not descripcion:
            result.skipped += 1
            continue

        responsable = val(row, "responsable") or None
        if responsable and responsable.lower() in ("pendiente", "unassigned", "sin asignar"):
            responsable = None

        estado = normalize_estado(val(row, "estado"))
        fecha_fin = parse_date(val(row, "fecha_fin"))
        fecha_completado = fecha_fin.isoformat() if (estado == "Completado" and fecha_fin) else None
        fecha_inicio = parse_date(val(row, "fecha_inicio"))

        result.tasks.append({
            "entidad": normalize_entidad(val(row, "entidad")),
            "proyecto": val(row, "proyecto") or None,
            "cliente": val(row, "cliente") or None,
            "descripcion": descripcion,
            "prioridad": normalize_prioridad(val(row, "prioridad")),
            "estado": estado,
            "responsable": responsable,
            "comentarios": val(row, "comentarios") or None,
            "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
            "fecha_fin": fecha_fin.isoformat() if fecha_fin else None,
            "fecha_completado": fecha_completado,
        })

    return result
