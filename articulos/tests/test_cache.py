"""Pruebas unitarias para el wrapper de caché."""

from __future__ import annotations

import json

from app.cache import ArticleCache


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    def get(self, key: str):
        return self.store.get(key)

    def setex(self, key: str, ttl: int, value: str) -> None:  # noqa: ARG002
        self.store[key] = value.encode("utf-8")

    def delete(self, key: str) -> None:
        self.store.pop(key, None)


def test_cache_roundtrip():
    fake = FakeRedis()
    cache = ArticleCache(fake)

    payload = {"id": "123", "title": "Cache"}
    cache.set("123", payload)

    raw = fake.store["article:123"].decode("utf-8")
    assert json.loads(raw)["title"] == "Cache"

    restored = cache.get("123")
    assert restored == payload

    cache.invalidate("123")
    assert cache.get("123") is None
