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


def test_default_jwt_secret_key():
    assert Settings.model_fields["jwt_secret_key"].default == "development-only-secret-key-32-bytes-long"
    assert len(Settings.model_fields["jwt_secret_key"].default) >= 32


def test_default_access_token_expire_minutes():
    assert Settings.model_fields["access_token_expire_minutes"].default == 30


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
    monkeypatch.setenv("JWT_SECRET_KEY", "super-secret-key")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "45")

    config = Settings()
    assert config.app_name == "OverrideApp"
    assert config.environment == "staging"
    assert config.debug is False
    assert config.log_level == "ERROR"
    assert config.jwt_secret_key == "super-secret-key"
    assert config.access_token_expire_minutes == 45


# --- Singleton accessibility ---


def test_settings_singleton_is_accessible():
    from app.core.config import settings

    assert settings.app_name == "BuildKit"


def test_settings_singleton_has_log_level():
    from app.core.config import settings

    assert settings.log_level == "INFO"


# --- Upload configuration ---


def test_default_max_upload_size():
    assert Settings.model_fields["max_upload_size"].default == 10_485_760


def test_default_allowed_upload_extensions():
    assert ".txt" in Settings.model_fields["allowed_upload_extensions"].default
    assert ".json" in Settings.model_fields["allowed_upload_extensions"].default


def test_max_upload_size_from_env(monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_SIZE", "5242880")
    assert Settings().max_upload_size == 5242880


def test_allowed_upload_extensions_singleton_has_defaults():
    from app.core.config import settings

    assert ".txt" in settings.allowed_upload_extensions
