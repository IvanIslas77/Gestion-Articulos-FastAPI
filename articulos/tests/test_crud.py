"""Pruebas unitarias para el repositorio de artículos."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.crud.article import ArticleRepository
from app.models.article import Article


@pytest.fixture()
def repository(db_session):
    return ArticleRepository(db_session)


def _build_article(**overrides):
    defaults = {
        "id": uuid.uuid4(),
        "title": "Título",
        "body": "Contenido",
        "tags": ["tag1", "tag2"],
        "author": "Autor",
    }
    defaults.update(overrides)
    return Article(**defaults)


def test_create_and_get_article(repository):
    article = _build_article()
    repository.create(article)
    repository.save()

    fetched = repository.get(str(article.id))
    assert fetched is not None
    assert fetched.title == article.title


def test_unique_constraint(repository):
    article = _build_article()
    repository.create(article)
    repository.save()

    duplicated = _build_article(title=article.title, author=article.author)
    repository.create(duplicated)
    with pytest.raises(IntegrityError):
        repository.save()


def test_list_and_filters(repository):
    for idx in range(3):
        repository.create(
            _build_article(
                title=f"Título {idx}",
                author="Autor" if idx < 2 else "Otro",
                tags=["python", "fastapi"] if idx != 1 else ["sqlalchemy"],
            )
        )
    repository.save()

    results = repository.list(author="Autor")
    assert len(results) == 2

    results = repository.list(tag="sqlalchemy")
    assert len(results) == 1

    results = repository.list(order_desc=False)
    assert len(results) == 3


def test_delete_article(repository):
    article = _build_article()
    repository.create(article)
    repository.save()

    repository.delete(article)
    repository.save()

    assert repository.get(str(article.id)) is None
