"""Inicialización del motor y la sesión de SQLAlchemy."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.postgres_dsn, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Proporciona una sesión de base de datos por solicitud."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
