"""Alembic environment configuration.

Configures the migration context at runtime using BuildKit's centralized
settings and SQLAlchemy Base metadata so that:
- the database URL comes from ``settings.database_url``
- autogeneration targets the existing ``Base.metadata``
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.database import Base
from app.models.user import User  # noqa: F401

# this is the Alembic Config object provided by the alembic runtime
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Reuse the existing SQLAlchemy declarative base so autogenerate detects
# models registered on Base.
target_metadata = Base.metadata


def get_url() -> str:
    """Return the database URL from centralized settings."""
    return settings.database_url


# Override the sqlalchemy.url placeholder in alembic.ini with the
# centralized settings value so configuration stays in one place.
config.set_main_option("sqlalchemy.url", get_url())


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Connects to the database and applies migrations.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
