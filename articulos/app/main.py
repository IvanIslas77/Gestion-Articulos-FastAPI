"""Punto de entrada para la aplicación FastAPI."""

from __future__ import annotations

from fastapi import FastAPI

from app.api import api_router
from app.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(api_router)


@app.get("/health", tags=["health"])  # pragma: no cover - endpoint trivial
async def health() -> dict[str, str]:
    """Verificación rápida del servicio."""

    return {"status": "ok"}
