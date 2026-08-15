import pytest

from app.core.config import Settings


# --- Default values (verified via field metadata, independent of environment) ---


def test_default_app_name():
    assert Settings.model_fields["app_name"].default == "BuildKit"


def test_default_environment():
    assert Settings.model_fields["environment"].default == "development"


def test_default_debug():
    assert Settings.model_fields["debug"].default is True


def test_default_log_level():
    assert Settings.model_fields["log_level"].default == "INFO"


# --- Environment variable overrides ---


def test_app_name_from_env(monkeypatch):
    monkeypatch.setenv("APP_NAME", "MyCustomApp")
    assert Settings().app_name == "MyCustomApp"


def test_environment_from_env(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    assert Settings().environment == "production"


def test_debug_from_env(monkeypatch):
    monkeypatch.setenv("DEBUG", "false")
    assert Settings().debug is False


def test_log_level_from_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    assert Settings().log_level == "WARNING"


def test_all_env_vars_override(monkeypatch):
    monkeypatch.setenv("APP_NAME", "OverrideApp")
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")

    config = Settings()
    assert config.app_name == "OverrideApp"
    assert config.environment == "staging"
    assert config.debug is False
    assert config.log_level == "ERROR"


# --- Singleton accessibility ---


def test_settings_singleton_is_accessible():
    from app.core.config import settings

    assert settings.app_name == "BuildKit"


def test_settings_singleton_has_log_level():
    from app.core.config import settings

    assert settings.log_level == "INFO"
