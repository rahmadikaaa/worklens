"""API endpoints for file uploads."""

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from app.config import Settings, get_settings
from app.models.schemas import FileUploadResponse
from app.services.upload_service import process_and_save_upload

router = APIRouter(tags=["Uploads"])


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload assessment file",
    description="Upload raw .json or .csv assessment file with size, type, and collision protection.",
)
@router.post(
    "/uploads",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def upload_assessment_file(
    file: UploadFile = File(..., description="Assessment file (.json or .csv)"),
    source_id: Optional[str] = Form(None, description="Optional custom source identifier"),
    settings: Settings = Depends(get_settings),
) -> FileUploadResponse:
    """Handle multipart file upload for JSON and CSV datasets."""
    result = await process_and_save_upload(
        file=file,
        upload_dir=settings.upload_dir,
        max_size_bytes=settings.max_upload_size_bytes,
        source_id=source_id,
    )
    return FileUploadResponse(**result)

