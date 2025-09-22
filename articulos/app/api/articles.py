
"""Endpoints REST para gestionar artículos."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import (
    enforce_api_key,
    get_article_service,
)
from app.schemas import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)
from app.services import ArticleService
from app.services.article_service import ArticleCreateData, ArticleDTO, ArticleUpdateData
from app.services.exceptions import ArticleAlreadyExistsError, ArticleNotFoundError

router = APIRouter(prefix="/articles", tags=["articles"], dependencies=[Depends(enforce_api_key)])


def _to_response(dto: ArticleDTO) -> ArticleResponse:
    """Convierte el DTO del servicio al esquema de respuesta del API."""
    return ArticleResponse.model_validate(dto.to_dict())


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(
    payload: ArticleCreate,
    service: ArticleService = Depends(get_article_service),
) -> ArticleResponse:
    try:
        dto = service.create(
            ArticleCreateData(
                title=payload.title,
                body=payload.body,
                tags=payload.tags,
                author=payload.author,
                published_at=payload.published_at,
            )
        )
    except ArticleAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return _to_response(dto)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: str,
    service: ArticleService = Depends(get_article_service),
) -> ArticleResponse:
    try:
        dto = service.get(article_id)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(dto)


@router.get("/", response_model=ArticleListResponse)
def list_articles_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    author: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: ArticleService = Depends(get_article_service),
) -> ArticleListResponse:
    order_desc = order != "asc"
    items, total = service.list(
        skip=skip,
        limit=limit,
        author=author,
        tag=tag,
        order_desc=order_desc,
    )
    return ArticleListResponse(
        items=[_to_response(dto) for dto in items],
        total=total,
        limit=limit,
        skip=skip,
    )


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: str,
    payload: ArticleUpdate,
    service: ArticleService = Depends(get_article_service),
) -> ArticleResponse:
    data = ArticleUpdateData(
        title=payload.title,
        body=payload.body,
        tags=payload.tags,
        author=payload.author,
        published_at=payload.published_at,
    )
    try:
        dto = service.update(article_id, data)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ArticleAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_response(dto)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_endpoint(
    article_id: str,
    service: ArticleService = Depends(get_article_service),
) -> Response:
    try:
        service.delete(article_id)
    except ArticleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
