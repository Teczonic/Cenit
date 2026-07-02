from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

def _get_database_url():
    url = os.getenv("DATABASE_URL", "")
    if url:
        # Vercel / Supabase Postgres uses postgres:// but SQLAlchemy needs postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    # On Vercel the filesystem is read-only; only /tmp is writable
    # Also fallback to /tmp if current dir is not writable
    if os.getenv("VERCEL") or not os.access(".", os.W_OK):
        return "sqlite:////tmp/cenit.db"
    return "sqlite:///./cenit.db"

DATABASE_URL = _get_database_url()

if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    # Strip sslmode from URL and pass via connect_args for psycopg2 compatibility
    _url = DATABASE_URL.replace("?sslmode=require", "").replace("&sslmode=require", "")
    engine = create_engine(
        _url,
        connect_args={"sslmode": "require"},
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
