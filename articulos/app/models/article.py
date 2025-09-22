"""Modelo SQLAlchemy para la tabla articles."""

import uuid

from sqlalchemy import Column, DateTime, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from app.database import Base


def _generate_uuid() -> uuid.UUID:
    """Genera un UUID4 como valor por defecto."""
    return uuid.uuid4()


class Article(Base):
    """Representa un artículo publicado en la plataforma."""

    __tablename__ = "articles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=_generate_uuid,
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    # Se usa ARRAY de texto para permitir múltiples etiquetas (ej. ['fastapi','redis']).
    tags = Column(ARRAY(String), nullable=False, server_default="{}")
    author = Column(String(255), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("title", "author", name="uq_articles_title_author"),
        Index("ix_articles_author", "author"),
        Index("ix_articles_published_at", "published_at"),
    )
