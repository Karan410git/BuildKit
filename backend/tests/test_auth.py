from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.database import Base, get_session
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_session] = override_get_session


client = TestClient(app)


def test_register_user_success():
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "securepassword"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["is_active"] is True
    assert "id" in data


def test_register_user_duplicate_email():
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "anotherpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exists"


def test_login_user_success():
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "securepassword"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_user_bad_password():
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_auth_me_with_valid_token():
    token_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "securepassword"},
    )
    token = token_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


def test_auth_me_with_invalid_token():
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication token"


def test_auth_me_with_non_integer_sub_returns_401():
    token = jwt.encode(
        {"sub": "not-an-integer", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
        settings.jwt_secret_key,
        algorithm="HS256",
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication token"


def test_jwt_secret_and_expiry_are_configured():
    assert settings.jwt_secret_key == "development-only-secret-key-32-bytes-long"
    assert len(settings.jwt_secret_key) >= 32
    assert settings.access_token_expire_minutes == 30
