
"""Pruebas de la capa de servicios con caché."""

from __future__ import annotations

from datetime import datetime

from app.services.article_service import ArticleCreateData, ArticleUpdateData
from app.services.exceptions import ArticleAlreadyExistsError, ArticleNotFoundError


def test_service_create_and_cache(service, cache):
    data = ArticleCreateData(
        title="Primer título",
        body="Contenido",
        tags=["fastapi"],
        author="Ana",
    )
    dto = service.create(data)

    cached = cache.get(dto.id)
    assert cached is not None
    assert cached["title"] == data.title


def test_service_get_uses_cache(service, cache):
    data = ArticleCreateData(
        title="Caché",
        body="Contenido",
        tags=["redis"],
        author="Ana",
    )
    created = service.create(data)

    # Eliminamos el registro de la base y dejamos sólo la caché.
    article = service._repository.get(created.id)
    service._repository.delete(article)
    service._repository.save()
    cache.set(created.id, created.to_dict())

    cached_dto = service.get(created.id)
    assert cached_dto.title == data.title


def test_service_unique_violation(service):
    data = ArticleCreateData(
        title="Único",
        body="Contenido",
        tags=[],
        author="Ana",
    )
    service.create(data)

    try:
        service.create(data)
    except ArticleAlreadyExistsError:
        assert True
    else:
        assert False, "Se esperaba ArticleAlreadyExistsError"


def test_service_update_and_delete(service, cache):
    created = service.create(
        ArticleCreateData(
            title="Actualizar",
            body="Viejo",
            tags=["tag"],
            author="Autor",
        )
    )

    updated = service.update(
        created.id,
        ArticleUpdateData(body="Nuevo", published_at=datetime.utcnow()),
    )
    assert updated.body == "Nuevo"

    service.delete(created.id)
    try:
        service.get(created.id)
    except ArticleNotFoundError:
        assert True
    else:
        assert False, "Se esperaba ArticleNotFoundError tras borrar"
