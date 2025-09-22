"""Dependencias comunes para la capa API."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.cache import ArticleCache, get_redis_client
from app.config import settings
from app.database import get_db
from app.services.article_service import ArticleService

API_KEY_HEADER = "x-api-key"
_api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


def get_db_session() -> Generator[Session, None, None]:
    """Inyecta una sesión de base de datos por petición HTTP."""

    yield from get_db()


def get_article_cache() -> ArticleCache:
    """Devuelve la instancia de caché configurada."""

    client = get_redis_client()
    return ArticleCache(client=client)


def get_article_service(
    db: Session = Depends(get_db_session),
    cache: ArticleCache = Depends(get_article_cache),
) -> ArticleService:
    """Construye la capa de servicios usando la sesión y el wrapper de caché."""
    return ArticleService(session=db, cache=cache)


def enforce_api_key(api_key: str | None = Depends(_api_key_header)) -> None:
    """Valida el API Key recibido en `x-api-key`."""

    expected = settings.api_key
    if expected and api_key == expected:
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key inválido")
