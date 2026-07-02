from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey,
    Enum as SAEnum, Text, Boolean
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class PriorityEnum(str, enum.Enum):
    urgente = "Urgente"
    alta = "Alta"
    media = "Media"
    baja = "Baja"
    pendiente = "Pendiente"


class StatusEnum(str, enum.Enum):
    no_iniciado = "No Iniciado"
    en_proceso = "En Proceso"
    pausado = "Pausado"
    completado = "Completado"


class EntityEnum(str, enum.Enum):
    xertify = "Xertify"
    xertiflow = "Xertiflow"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(50), default="developer")
    hourly_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    entity = Column(SAEnum(EntityEnum), nullable=False)
    contact_email = Column(String(150))
    is_internal = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    tasks = relationship("Task", back_populates="client")


class Sprint(Base):
    __tablename__ = "sprints"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Float, default=0.0)
    entity = Column(SAEnum(EntityEnum))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    tasks = relationship("Task", back_populates="sprint")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    entity = Column(SAEnum(EntityEnum), nullable=False)
    project = Column(String(100))
    description = Column(Text, nullable=False)
    priority = Column(SAEnum(PriorityEnum), default=PriorityEnum.media)
    status = Column(SAEnum(StatusEnum), default=StatusEnum.no_iniciado)
    start_date = Column(Date)
    end_date = Column(Date)
    completed_at = Column(Date)

    estimated_hours = Column(Float, default=0.0)
    actual_hours = Column(Float, default=0.0)
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)

    comments = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)

    assignee = relationship("User", back_populates="tasks", foreign_keys=[assignee_id])
    client = relationship("Client", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    time_logs = relationship("TimeLog", back_populates="task", cascade="all, delete-orphan")

    @property
    def lead_time_days(self):
        if self.start_date and self.completed_at:
            return (self.completed_at - self.start_date).days
        return None

    @property
    def eisenhower_quadrant(self):
        urgent = self.priority == PriorityEnum.urgente or self.status == StatusEnum.en_proceso
        important = self.priority in (PriorityEnum.alta, PriorityEnum.urgente)
        if urgent and important:
            return "Q1"
        elif not urgent and important:
            return "Q2"
        elif urgent and not important:
            return "Q3"
        return "Q4"


class TimeLog(Base):
    __tablename__ = "time_logs"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hours = Column(Float, nullable=False)
    log_date = Column(Date, nullable=False)
    note = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="time_logs")
    user = relationship("User")
