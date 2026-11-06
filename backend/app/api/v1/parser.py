"""API endpoints for reading and parsing uploaded assessment files (P2)."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.config import Settings, get_settings
from app.models.schemas import FileParseResponse
from app.services.parser_service import parse_assessment_file
from app.services.snapshot_service import get_snapshot_by_id

router = APIRouter(tags=["Parsing"])


@router.post(
    "/parse",
    response_model=FileParseResponse,
    summary="Parse an uploaded assessment file or snapshot via query parameter",
    description="Read and parse an uploaded JSON or CSV file by providing ?filename=... or ?snapshot_id=...",
)
@router.get(
    "/parse",
    response_model=FileParseResponse,
    include_in_schema=False,
)
def parse_file_query_endpoint(
    filename: Optional[str] = Query(None, description="Name of the file in upload directory"),
    snapshot_id: Optional[str] = Query(None, description="Snapshot ID to parse"),
    settings: Settings = Depends(get_settings),
) -> FileParseResponse:
    """Parse specified assessment file or snapshot using query parameter."""
    if snapshot_id:
        snapshot = get_snapshot_by_id(snapshot_id, settings.upload_dir)
        target_filename = snapshot.stored_filename
    elif filename:
        target_filename = filename
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'filename' or 'snapshot_id' query parameter must be provided.",
        )

    result = parse_assessment_file(
        filename=target_filename,
        upload_dir=settings.upload_dir,
    )
    return FileParseResponse(**result)


@router.post(
    "/parse/{filename:path}",
    response_model=FileParseResponse,
    summary="Parse an uploaded assessment file by filename path",
    description="Read and parse an uploaded JSON or CSV file from the upload directory, returning metadata and column structure.",
)
@router.get(
    "/parse/{filename:path}",
    response_model=FileParseResponse,
    summary="Parse an uploaded assessment file by filename path (GET)",
    description="Read and parse an uploaded JSON or CSV file from the upload directory, returning metadata and column structure.",
)
def parse_file_endpoint(
    filename: str,
    settings: Settings = Depends(get_settings),
) -> FileParseResponse:
    """Parse specified assessment file from upload storage."""
    result = parse_assessment_file(
        filename=filename,
        upload_dir=settings.upload_dir,
    )
    return FileParseResponse(**result)
