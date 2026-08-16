import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings

router = APIRouter()


def _sanitize_filename(filename: str) -> str:
    return os.path.basename(filename).replace("\x00", "")


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    safe_filename = _sanitize_filename(file.filename)
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    extension = Path(safe_filename).suffix.lower()
    allowed = {item.lower() for item in settings.allowed_upload_extensions}
    if extension not in allowed:
        raise HTTPException(status_code=400, detail=f"File extension '{extension}' is not allowed")
    content = await file.read()
    size = len(content)
    if size > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {size} bytes exceeds maximum allowed {settings.max_upload_size} bytes",
        )
    return {"filename": safe_filename, "content_type": file.content_type, "size": size, "extension": extension}
