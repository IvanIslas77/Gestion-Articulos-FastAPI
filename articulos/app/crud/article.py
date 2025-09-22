
"""Operaciones CRUD encapsuladas para la entidad `Article`."""

from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.article import Article


class ArticleRepository:
    """Repositorio orientado a la entidad `Article`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def _base_query(self) -> Select[tuple[Article]]:
        return select(Article)

    def _apply_filters(
        self,
        stmt: Select[tuple[Article]],
        *,
        author: str | None = None,
        tag: str | None = None,
    ) -> Select[tuple[Article]]:
        if author:
            stmt = stmt.where(Article.author == author)
        if tag:
            stmt = stmt.where(Article.tags.contains([tag]))
        return stmt

    def get(self, article_id: str) -> Optional[Article]:
        return self._session.get(Article, article_id)

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        author: str | None = None,
        tag: str | None = None,
        order_desc: bool = True,
    ) -> list[Article]:
        stmt = self._base_query()
        stmt = self._apply_filters(stmt, author=author, tag=tag)
        order_column = (
            Article.published_at.desc().nullslast()
            if order_desc
            else Article.published_at.asc().nullsfirst()
        )
        stmt = stmt.order_by(order_column).offset(skip).limit(limit)
        result = self._session.execute(stmt)
        return list(result.scalars().all())

    def count(
        self,
        *,
        author: str | None = None,
        tag: str | None = None,
    ) -> int:
        stmt = select(func.count(Article.id))
        stmt = self._apply_filters(stmt, author=author, tag=tag)
        return self._session.execute(stmt).scalar_one()

    def create(self, article: Article) -> Article:
        self._session.add(article)
        return article

    def update(self, article: Article, **fields: object) -> Article:
        for key, value in fields.items():
            setattr(article, key, value)
        self._session.add(article)
        return article

    def delete(self, article: Article) -> None:
        self._session.delete(article)

    def save(self) -> None:
        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise

    def refresh(self, article: Article) -> Article:
        self._session.refresh(article)
        return article

    def sync(self, article: Article, *, fields: Iterable[str] | None = None) -> Article:
        self._session.flush()
        if fields:
            self._session.refresh(article, attribute_names=list(fields))
        else:
            self._session.refresh(article)
        return article
