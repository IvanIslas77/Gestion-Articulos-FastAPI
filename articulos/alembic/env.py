"""Archivo de configuración para ejecutar migraciones con Alembic."""

import os

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.database import Base

# Metadata de nuestros modelos SQLAlchemy.
target_metadata = Base.metadata


def get_url() -> str:
    """Resuelve la URL de conexión a la base de datos."""
    return os.getenv(
        "DATABASE_URL",
        context.config.get_main_option(
            "sqlalchemy.url",
        ),
    )


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'."""
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online'."""
    configuration = context.config.get_section(context.config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
