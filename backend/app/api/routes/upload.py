"""Generic file upload endpoint.

Accepts a single file upload, validates size and extension,
sanitizes the filename, and returns generic metadata.
Files are validated in memory only — they are not persisted.
"""

import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings

router = APIRouter()


def _sanitize_filename(filename: str) -> str:
    """Strip path components and dangerous characters from a filename."""
    # Remove directory traversal components
    filename = os.path.basename(filename)
    # Remove null bytes which can truncate filenames in some filesystems
    filename = filename.replace("\x00", "")
    return filename


def _get_extension(filename: str) -> str:
    """Return the lowercase file extension including the leading dot."""
    return Path(filename).suffix.lower()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    """Upload a file and return generic metadata.

    The file is validated in memory only — it is not persisted to disk
    or the database.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    safe_filename = _sanitize_filename(file.filename)
    if not safe_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename",
        )

    # Validate file extension (case-insensitive)
    extension = _get_extension(safe_filename)
    allowed = {ext.lower() for ext in settings.allowed_upload_extensions}
    if extension not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{extension}' is not allowed",
        )

    # Read content into memory for size validation
    content = await file.read()
    size = len(content)
    if size > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {size} bytes exceeds maximum allowed {settings.max_upload_size} bytes",
        )

    return {
        "filename": safe_filename,
        "content_type": file.content_type,
        "size": size,
        "extension": extension,
    }
