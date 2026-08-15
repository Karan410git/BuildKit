from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app


def test_app_is_fastapi_instance():
    assert isinstance(app, FastAPI)


def test_app_title_from_settings():
    from app.core.config import settings

    assert app.title == settings.app_name


def test_app_debug_from_settings():
    from app.core.config import settings

    assert app.debug == settings.debug


def test_health_endpoint_returns_success():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_content_type():
    client = TestClient(app)
    response = client.get("/health")
    assert response.headers["content-type"].startswith("application/json")
