from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Text, ForeignKey, Float,
    Boolean, UniqueConstraint,
)
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(50), unique=True, index=True, nullable=False)
    name            = Column(String(100), nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role            = Column(String(20), default="member")  # admin | member
    color           = Column(String(7), default="#2563EB")
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

class Task(Base):
    __tablename__ = "tasks"
    id           = Column(Integer, primary_key=True, index=True)
    entidad      = Column(String(50), nullable=False)
    proyecto     = Column(String(80))
    cliente      = Column(String(100))
    descripcion  = Column(Text, nullable=False)
    prioridad    = Column(String(20), default="Media")   # Urgente | Alta | Media | Baja
    estado       = Column(String(30), default="No Iniciado")  # No Iniciado | En Proceso | Pausado | Completado
    responsable  = Column(String(80))
    comentarios  = Column(Text)
    fecha_inicio = Column(DateTime(timezone=True))
    fecha_fin    = Column(DateTime(timezone=True))
    fecha_completado = Column(DateTime(timezone=True))
    created_by   = Column(String(80))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def lead_time_days(self):
        if self.fecha_inicio and self.fecha_completado:
            delta = self.fecha_completado - self.fecha_inicio
            return round(delta.total_seconds() / 86400, 1)
        return None

    @property
    def eisenhower(self):
        from datetime import datetime, timezone
        importante = self.prioridad in ("Urgente", "Alta")
        urgente_tiempo = False
        if self.fecha_fin:
            now = datetime.now(timezone.utc)
            ff = self.fecha_fin if self.fecha_fin.tzinfo else self.fecha_fin.replace(tzinfo=timezone.utc)
            dias_restantes = (ff - now).days
            urgente_tiempo = dias_restantes <= 7
        elif self.prioridad == "Urgente":
            urgente_tiempo = True
        if importante and urgente_tiempo:      return "Q1"
        if importante and not urgente_tiempo:  return "Q2"
        if not importante and urgente_tiempo:  return "Q3"
        return "Q4"

    @property
    def risk_score(self):
        # ── Probabilidad + Test base por área (tabla_de_impacto.csv) ──────────
        # Prob escala 1-4 → normalizada a 1-10: round(1 + (prob-1)/3 * 9)
        PROYECTO_MAP = {
            "Generador":   {"prob": 10, "test_base": 15},
            "Desarrollo":  {"prob": 10, "test_base": 20},
            "Operaciones": {"prob":  7, "test_base": 30},
            "Wallet":      {"prob":  7, "test_base": 25},
            "Scrapi":      {"prob":  7, "test_base": 20},
            "Soporte":     {"prob":  4, "test_base": 50},
            "Marketing":   {"prob":  4, "test_base": 60},
            "Comercial":   {"prob":  1, "test_base": 70},
        }
        proy = PROYECTO_MAP.get(self.proyecto or "", {"prob": 5, "test_base": 25})
        probabilidad = proy["prob"]

        # ── Impacto 1-10 por cliente (clientes_porcentaje_consolidado.csv) ────
        # Fórmula: round(1 + (pct / 8.88) * 9), máx 10; Interno = 1
        CLIENTE_IMPACTO = {
            "uniandes": 10, "inlearning": 9, "javeriana": 7, "upb": 7,
            "eia": 6, "cmv": 6, "eia firmas": 4, "ibero": 4,
            "javeriana cali": 3, "andes": 3, "valentina": 3,
            "pedronal": 3, "provida": 3, "icesi": 3, "andes admin": 3,
            "externado": 3, "brightspace": 2, "u rosario": 2, "eafit": 2,
            "scare": 2, "inlearning - eva": 2, "enap": 2, "pilsa": 2,
            "uniandinos": 2, "constructora": 2, "universidad de antioquia": 2,
            "javeriana educacion continua": 2, "cuauhtemoc": 2,
            "colfuturo": 2, "utb": 2, "camara comercio exterior": 2,
            "andes - simon": 2, "costa rica": 2, "queretaro": 2,
            "corposinfronteras": 2, "h2a": 2, "funcicolombia": 2,
            "casa de moneda": 2, "edumed": 2, "provida - scare": 2,
            "konrad lorenz": 1, "uniminuto": 1, "u sabana": 1,
            "universidad del rosario": 1, "universidad del valle": 1,
            "iberoamerica": 1, "escuela de ingenieros": 1, "anahuac": 1,
            "netec": 1, "griky": 1, "constructora bolivar": 1, "zuana": 1,
            "lbsmobile": 1, "conmeva": 1, "conecta logistica - chile": 1,
        }
        INTERNOS = {"interno", "", "sin definir", "javeriana-interno",
                    "wallet", "api", "comunidades", "firmas", "finanzas",
                    "redes sociales.", "mobile", "general", "comercial",
                    "adriana xerti", "liliana"}
        c = (self.cliente or "").strip().lower()
        if c in INTERNOS:
            impacto = 1
        else:
            impacto = CLIENTE_IMPACTO.get(c, 3)

        # ── Cobertura test: base del área ajustada por estado ─────────────────
        test_base = proy["test_base"]
        cobertura_map = {
            "Completado":   100,
            "En Proceso":   min(test_base + 20, 90),
            "Pausado":      test_base,
            "No Iniciado":  max(test_base - 10, 0),
        }
        cobertura = cobertura_map.get(self.estado, test_base) / 100

        # ── Risk Score 0-100 ──────────────────────────────────────────────────
        return round(probabilidad * impacto * (1 - cobertura) / 10, 1)


class TaskStateTransition(Base):
    """Historial de cambios de estado — cimiento del motor de flujo de Cenit.

    Cada transición registrada desbloquea lead time real, cycle time, aging,
    flow efficiency y las métricas DORA/Lean, sin recalcular desde columnas sueltas.
    """
    __tablename__ = "task_state_transitions"
    id         = Column(Integer, primary_key=True, index=True)
    task_id    = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    from_state = Column(String(30))                       # None en la transición inicial
    to_state   = Column(String(30), nullable=False)
    changed_by = Column(String(80))                       # username, consistente con tasks.created_by
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    reason     = Column(Text)


# ── OKRs: capa de dirección (tareas → resultados) ──────────────────────────────

class OkrCycle(Base):
    __tablename__ = "okr_cycles"
    id           = Column(Integer, primary_key=True, index=True)
    nombre       = Column(String(40), nullable=False)     # ej: "Q3 2026"
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin    = Column(Date, nullable=False)
    estado       = Column(String(20), default="activo")   # activo | cerrado


class Objective(Base):
    __tablename__ = "objectives"
    id       = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("okr_cycles.id", ondelete="CASCADE"), nullable=False, index=True)
    titulo   = Column(String(200), nullable=False)
    owner    = Column(String(80))                          # username del responsable
    entidad  = Column(String(50))


class KeyResult(Base):
    __tablename__ = "key_results"
    id            = Column(Integer, primary_key=True, index=True)
    objective_id  = Column(Integer, ForeignKey("objectives.id", ondelete="CASCADE"), nullable=False, index=True)
    titulo        = Column(String(200), nullable=False)
    valor_inicial = Column(Float, nullable=False, default=0)
    valor_meta    = Column(Float, nullable=False)
    valor_actual  = Column(Float, nullable=False, default=0)
    unidad        = Column(String(20))


class TaskKeyResult(Base):
    """Vincula una tarea a un key result — base del alignment ratio."""
    __tablename__ = "task_key_results"
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    kr_id   = Column(Integer, ForeignKey("key_results.id", ondelete="CASCADE"), primary_key=True)


# ── Motor de métricas / KPIs ───────────────────────────────────────────────────

class MetricDefinition(Base):
    """Catálogo: qué KPI existe y cómo se evalúa su semáforo."""
    __tablename__ = "metric_definitions"
    id            = Column(Integer, primary_key=True, index=True)
    clave         = Column(String(60), unique=True, nullable=False)  # 'lead_time_p85'
    nombre        = Column(String(120), nullable=False)
    fuente        = Column(String(40), nullable=False, default="manual")  # manual | flow | okr
    entidad       = Column(String(50))
    direccion     = Column(String(10), nullable=False)   # up | down | band
    meta          = Column(Float)
    umbral_alerta = Column(Float)
    banda_min     = Column(Float)
    banda_max     = Column(Float)
    unidad        = Column(String(20))
    owner         = Column(String(80))
    activa        = Column(Boolean, nullable=False, default=True)


class MetricSnapshot(Base):
    """Serie temporal inmutable: el valor de un KPI en un periodo. Append-only."""
    __tablename__ = "metric_snapshots"
    id             = Column(Integer, primary_key=True, index=True)
    metric_id      = Column(Integer, ForeignKey("metric_definitions.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    periodo_inicio = Column(Date, nullable=False)
    periodo_fin    = Column(Date, nullable=False)
    valor          = Column(Float, nullable=False)
    estado         = Column(String(10), nullable=False)  # verde | ambar | rojo | sin_datos
    calculado_en   = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("metric_id", "periodo_inicio", "periodo_fin",
                                       name="uq_metric_periodo"),)
