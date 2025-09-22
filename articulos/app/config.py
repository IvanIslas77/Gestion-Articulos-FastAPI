"""Configuración central de la aplicación."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Agrupa la configuración de la app cargada desde variables de entorno."""

    # Datos básicos expuestos en la documentación /health.
    app_name: str = Field(default="Articles Management API", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")

    # Clave API utilizada por los endpoints protegidos.
    api_key: str = Field(default="local-dev-key", env="API_KEY")

    # Parámetros de conexión a PostgreSQL (servicio `db` en docker-compose).
    postgres_host: str = Field(default="db", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="articles", env="POSTGRES_DB")

    # URL que consume el cliente Redis (servicio `redis`).
    redis_url: str = Field(default="redis://redis:6379/0", env="REDIS_URL")
    database_url: str | None = Field(default=None, env="DATABASE_URL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore",)

    @property
    def postgres_dsn(self) -> str:
        """Construye el DSN para SQLAlchemy cuando no se especifica DATABASE_URL."""

        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache()
def get_settings() -> Settings:
    """Retorna una instancia cacheada de Settings."""

    return Settings()


settings = get_settings()
