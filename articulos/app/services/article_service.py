
"""Servicios de dominio para manejar artículos con soporte de caché."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.cache import ArticleCache
from app.models.article import Article

from .exceptions import ArticleAlreadyExistsError, ArticleNotFoundError


@dataclass(slots=True)
class ArticleDTO:
    """Representación serializable de un artículo."""

    id: str
    title: str
    body: str
    tags: List[str]
    author: str
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, article: Article) -> "ArticleDTO":
        return cls(
            id=str(article.id),
            title=article.title,
            body=article.body,
            tags=list(article.tags or []),
            author=article.author,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ArticleDTO":
        return cls(
            id=payload["id"],
            title=payload["title"],
            body=payload["body"],
            tags=list(payload.get("tags", [])),
            author=payload["author"],
            published_at=(
                datetime.fromisoformat(payload["published_at"])
                if payload.get("published_at")
                else None
            ),
            created_at=datetime.fromisoformat(payload["created_at"]),
            updated_at=datetime.fromisoformat(payload["updated_at"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["published_at"] = self.published_at.isoformat() if self.published_at else None
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data


@dataclass(slots=True)
class ArticleCreateData:
    title: str
    body: str
    tags: List[str]
    author: str
    published_at: Optional[datetime] = None


@dataclass(slots=True)
class ArticleUpdateData:
    title: Optional[str] = None
    body: Optional[str] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None


class ArticleService:
    """Orquesta repositorio y caché para operaciones de artículos."""

    def __init__(
        self,
        session: Session,
        *,
        cache: Optional[ArticleCache] = None,
    ) -> None:
        from app.crud.article import ArticleRepository

        self._repository = ArticleRepository(session)
        self._cache = cache

    def _store_in_cache(self, dto: ArticleDTO) -> None:
        if self._cache is not None:
            self._cache.set(dto.id, dto.to_dict())

    def _evict_cache(self, article_id: str) -> None:
        if self._cache is not None:
            self._cache.invalidate(article_id)

    def create(self, data: ArticleCreateData) -> ArticleDTO:
        article = Article(
            title=data.title,
            body=data.body,
            tags=data.tags,
            author=data.author,
            published_at=data.published_at,
        )

        self._repository.create(article)
        try:
            self._repository.save()
        except IntegrityError as exc:
            raise ArticleAlreadyExistsError("Ya existe un artículo con el mismo título y autor") from exc

        self._repository.refresh(article)
        dto = ArticleDTO.from_model(article)
        self._store_in_cache(dto)
        return dto

    def get(self, article_id: str) -> ArticleDTO:
        if self._cache is not None:
            cached = self._cache.get(article_id)
            if cached:
                return ArticleDTO.from_dict(cached)

        article = self._repository.get(article_id)
        if article is None:
            raise ArticleNotFoundError("Artículo no encontrado")

        dto = ArticleDTO.from_model(article)
        self._store_in_cache(dto)
        return dto

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        order_desc: bool = True,
    ) -> Tuple[List[ArticleDTO], int]:
        articles = self._repository.list(
            skip=skip,
            limit=limit,
            author=author,
            tag=tag,
            order_desc=order_desc,
        )
        total = self._repository.count(author=author, tag=tag)
        return [ArticleDTO.from_model(article) for article in articles], total

    def update(self, article_id: str, data: ArticleUpdateData) -> ArticleDTO:
        article = self._repository.get(article_id)
        if article is None:
            raise ArticleNotFoundError("Artículo no encontrado")

        fields: Dict[str, Any] = {}
        if data.title is not None:
            fields["title"] = data.title
        if data.body is not None:
            fields["body"] = data.body
        if data.tags is not None:
            fields["tags"] = data.tags
        if data.author is not None:
            fields["author"] = data.author
        if data.published_at is not None:
            fields["published_at"] = data.published_at

        self._repository.update(article, **fields)
        try:
            self._repository.save()
        except IntegrityError as exc:
            raise ArticleAlreadyExistsError("Ya existe un artículo con el mismo título y autor") from exc

        self._repository.refresh(article)
        dto = ArticleDTO.from_model(article)
        self._store_in_cache(dto)
        return dto

    def delete(self, article_id: str) -> None:
        article = self._repository.get(article_id)
        if article is None:
            raise ArticleNotFoundError("Artículo no encontrado")

        self._repository.delete(article)
        self._repository.save()
        self._evict_cache(article_id)
