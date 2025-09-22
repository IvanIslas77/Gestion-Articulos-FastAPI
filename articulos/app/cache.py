"""Wrapper simple para operaciones de caché basadas en Redis."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import redis

from app.config import settings

DEFAULT_TTL_SECONDS = 120


class ArticleCache:
    """Provee operaciones `get` / `set` / `invalidate` para artículos."""

    def __init__(self, client: redis.Redis, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        # El cliente Redis se inyecta desde las dependencias (permite usar stubs en tests).
        self._client = client
        self._ttl = ttl_seconds

    @staticmethod
    def _key(article_id: str) -> str:
        return f"article:{article_id}"

    def get(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Lee del cache; si no existe devuelve ``None``."""
        raw = self._client.get(self._key(article_id))
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
            return None

    def set(self, article_id: str, payload: Dict[str, Any]) -> None:
        """Serializa el payload a JSON y lo almacena con expiración."""
        self._client.setex(self._key(article_id), self._ttl, json.dumps(payload))

    def invalidate(self, article_id: str) -> None:
        """Elimina la clave del cache (se usa tras borrar o actualizar)."""
        self._client.delete(self._key(article_id))


def get_redis_client() -> redis.Redis:
    """Devuelve un cliente Redis conectado usando la configuración de la app."""
    return redis.Redis.from_url(settings.redis_url, decode_responses=False)
