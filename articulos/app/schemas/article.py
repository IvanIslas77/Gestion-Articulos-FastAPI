"""Esquemas Pydantic para requests y responses del recurso `Article`."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _coerce_tags(value: Optional[str | List[str]]) -> List[str]:
    """Acepta tags como lista o string separado por `;` y devuelve una lista depurada."""
    if value is None:
        return []
    if isinstance(value, list):
        return [tag.strip() for tag in value if tag and tag.strip()]
    if isinstance(value, str):
        if not value.strip():
            return []
        return [tag.strip() for tag in value.split(";") if tag.strip()]
    msg = "Formato inválido para tags"
    raise ValueError(msg)


class ArticleBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    tags: List[str] = Field(default_factory=list)
    author: str = Field(min_length=1, max_length=255)
    published_at: Optional[datetime] = None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Optional[str | List[str]]) -> List[str]:
        return _coerce_tags(value)


class ArticleCreate(ArticleBase):
    """Payload para crear un artículo."""


class ArticleUpdate(BaseModel):
    """Payload para actualizar campos opcionales de un artículo."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    body: Optional[str] = Field(default=None, min_length=1)
    tags: Optional[List[str] | str] = None
    author: Optional[str] = Field(default=None, min_length=1, max_length=255)
    published_at: Optional[datetime] = None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Optional[str | List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        return _coerce_tags(value)


class ArticleResponse(ArticleBase):
    """Respuesta estándar del API para artículos individuales."""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    """Respuesta para listados paginados."""

    items: List[ArticleResponse]
    total: int
    limit: int
    skip: int
