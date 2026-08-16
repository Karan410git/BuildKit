"""Tests for Alembic migration configuration.

These tests verify that Alembic is correctly wired to BuildKit's
centralized settings and SQLAlchemy metadata, without requiring
a running PostgreSQL server.
"""

from pathlib import Path

from alembic.config import Config

from app.core.config import settings
from app.db.database import Base

BACKEND_DIR = Path(__file__).resolve().parent.parent
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
ENV_PY = BACKEND_DIR / "alembic" / "env.py"


# --- Configuration file tests ---


def test_alembic_ini_exists():
    """Verify the Alembic configuration file exists."""
    assert ALEMBIC_INI.exists()


def test_alembic_config_loads():
    """Verify the Alembic Config object can be created from the ini file."""
    config = Config(str(ALEMBIC_INI))
    assert config is not None


def test_script_location_configured():
    """Verify script_location is set in the ini."""
    config = Config(str(ALEMBIC_INI))
    assert config.get_main_option("script_location") is not None


def test_env_py_exists():
    """Verify the env.py configuration module exists."""
    assert ENV_PY.exists()


# --- Integration tests (no database required) ---


def test_env_imports_settings():
    """Verify env.py imports settings from the centralized config module."""
    source = ENV_PY.read_text()
    assert "from app.core.config import settings" in source


def test_env_imports_base_metadata():
    """Verify env.py imports Base from the existing database module."""
    source = ENV_PY.read_text()
    assert "from app.db.database import Base" in source


def test_env_sets_target_metadata():
    """Verify env.py assigns Base.metadata as target_metadata."""
    source = ENV_PY.read_text()
    assert "target_metadata = Base.metadata" in source


def test_env_overrides_url_from_settings():
    """Verify env.py calls set_main_option with the settings database URL."""
    source = ENV_PY.read_text()
    assert "config.set_main_option" in source
    assert "sqlalchemy.url" in source
    assert "settings.database_url" in source


def test_offline_migration_runs_without_database():
    """Verify offline migration mode initializes without a database connection.

    Uses Alembic's ``sql=True`` flag which invokes run_migrations_offline()
    and generates SQL without ever connecting to PostgreSQL. The fact that
    settings.database_url is used as the URL and Base.metadata is the target
    is validated by the successful offline context configuration.
    """
    from alembic import command

    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    # sql=True runs in offline mode — no database connection is made
    command.upgrade(config, "head", sql=True)
    # env.py overrides the ini URL at runtime with settings.database_url
    assert config.get_main_option("sqlalchemy.url") == settings.database_url


def test_no_migration_scripts_yet():
    """Verify the versions directory exists and is empty (no domain models yet)."""
    versions_dir = BACKEND_DIR / "alembic" / "versions"
    assert versions_dir.is_dir()
    migration_files = list(versions_dir.glob("*.py"))
    assert migration_files == [], "No migration scripts should exist yet"
