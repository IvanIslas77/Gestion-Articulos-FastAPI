"""Fixtures compartidas para la suite de pruebas."""

from __future__ import annotations

import os
import uuid
from collections.abc import Generator
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import enforce_api_key, get_article_service, get_db_session
from app.config import settings
from app.database import Base
from app.main import app
from app.services import ArticleService

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@db:5432/articles_test",
)


def _ensure_uuid() -> str:
    return str(uuid.uuid4())


class DummyCache:
    """Cache en memoria que imita a Redis para pruebas."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _key(article_id: str) -> str:
        return f"article:{article_id}"

    def get(self, article_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(self._key(article_id))

    def set(self, article_id: str, payload: Dict[str, Any]) -> None:
        self._store[self._key(article_id)] = payload

    def invalidate(self, article_id: str) -> None:
        self._store.pop(self._key(article_id), None)


@pytest.fixture(scope="session")
def engine() -> Generator:
    engine = create_engine(TEST_DATABASE_URL, future=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def create_schema(engine) -> Generator:
    import app.models  # noqa: F401 - asegura el registro de modelos

    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture()
def db_session(engine, session_factory) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = session_factory(bind=connection)
    try:
        yield session
        session.commit()
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def cache() -> DummyCache:
    return DummyCache()


@pytest.fixture()
def service(db_session: Session, cache: DummyCache) -> Generator[ArticleService, None, None]:
    service = ArticleService(session=db_session, cache=cache)
    yield service


@pytest.fixture()
def client(db_session: Session, cache: DummyCache) -> Generator[TestClient, None, None]:
    original_api_key = settings.api_key
    settings.api_key = "test-key"

    def override_db() -> Generator[Session, None, None]:
        yield db_session

    def override_service() -> ArticleService:
        return ArticleService(session=db_session, cache=cache)

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_article_service] = override_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    settings.api_key = original_api_key


@pytest.fixture()
def api_headers() -> Dict[str, str]:
    return {"x-api-key": "test-key"}
