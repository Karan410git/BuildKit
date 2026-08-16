"""Tests for the generic upload API endpoint.

These tests validate file upload, extension checking, size limits,
and filename sanitization without requiring a database or filesystem
storage.
"""

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


# --- Happy path ---


def test_upload_valid_file():
    """A valid file upload returns 200 with metadata."""
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["content_type"] == "text/plain"
    assert data["size"] == 11
    assert data["extension"] == ".txt"


def test_upload_empty_file():
    """An empty file with a valid extension returns 200 with size 0."""
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("empty.json", b"", "application/json")},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["size"] == 0
    assert data["extension"] == ".json"


def test_upload_extension_case_insensitive():
    """File extension matching is case-insensitive."""
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("IMAGE.PNG", b"data", "image/png")},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["extension"] == ".png"


# --- Validation errors ---


def test_upload_missing_file():
    """No file in the request returns 422."""
    client = TestClient(app)
    response = client.post("/upload")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_empty_filename():
    """An empty filename returns 422 (FastAPI multipart validation)."""
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("", b"hello", "text/plain")},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_disallowed_extension():
    """A file with a disallowed extension returns 400."""
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("script.exe", b"payload", "application/octet-stream")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_upload_no_extension():
    """A file with no extension returns 400."""
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("README", b"content", "text/plain")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_upload_oversized_file():
    """A file exceeding the max size returns 413."""
    client = TestClient(app)
    large_content = b"x" * 11_000_000  # 11 MB, exceeds default 10 MB limit
    response = client.post(
        "/upload",
        files={"file": ("large.txt", large_content, "text/plain")},
    )
    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


# --- Filename sanitization ---


def test_upload_filename_path_traversal_sanitized():
    """Path traversal components in filename are stripped."""
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("../../etc/passwd.txt", b"content", "text/plain")},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["filename"] == "passwd.txt"


def test_upload_filename_null_bytes_stripped():
    """Null bytes in filename are removed."""
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("test\x00.txt", b"content", "text/plain")},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "\x00" not in response.json()["filename"]


# --- Response structure ---


def test_upload_response_keys():
    """Upload response contains all expected metadata keys."""
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert set(data.keys()) == {"filename", "content_type", "size", "extension"}
