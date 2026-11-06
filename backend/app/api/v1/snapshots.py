"""API endpoints for source snapshot versioning, history, and secure access (P3)."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from app.config import Settings, get_settings
from app.models.schemas import FileParseResponse, SourceSnapshot
from app.services.parser_service import parse_assessment_file
from app.services.snapshot_service import (
    get_snapshot_by_id,
    list_snapshots,
    resolve_snapshot_file_path,
)

router = APIRouter(prefix="/snapshots", tags=["Source Versioning & Snapshots"])


@router.get(
    "",
    response_model=list[SourceSnapshot],
    summary="List source snapshots",
    description="Retrieve all registered source snapshots ordered chronologically (newest first).",
)
def list_source_snapshots_endpoint(
    source_id: Optional[str] = Query(None, description="Filter snapshots by source identifier"),
    settings: Settings = Depends(get_settings),
) -> list[SourceSnapshot]:
    """Retrieve list of all source snapshots."""
    return list_snapshots(upload_dir=settings.upload_dir, source_id=source_id)


@router.get(
    "/{snapshot_id}",
    response_model=SourceSnapshot,
    summary="Get source snapshot metadata",
    description="Retrieve detailed metadata for a specific snapshot by its ID.",
)
def get_snapshot_metadata_endpoint(
    snapshot_id: str,
    settings: Settings = Depends(get_settings),
) -> SourceSnapshot:
    """Retrieve metadata of a single snapshot."""
    return get_snapshot_by_id(snapshot_id=snapshot_id, upload_dir=settings.upload_dir)


@router.get(
    "/{snapshot_id}/content",
    summary="View snapshot file content",
    description="Securely access the byte-for-byte unmodified snapshot file content.",
)
def get_snapshot_content_endpoint(
    snapshot_id: str,
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """Securely stream snapshot file contents."""
    snapshot = get_snapshot_by_id(snapshot_id=snapshot_id, upload_dir=settings.upload_dir)
    file_path = resolve_snapshot_file_path(snapshot=snapshot, upload_dir=settings.upload_dir)

    media_type = "application/json" if snapshot.file_format == "json" else "text/csv"
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=snapshot.original_filename,
        content_disposition_type="inline",
    )


@router.get(
    "/{snapshot_id}/download",
    summary="Download snapshot file",
    description="Download the original snapshot file as an attachment.",
)
def download_snapshot_endpoint(
    snapshot_id: str,
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """Securely download snapshot file as attachment."""
    snapshot = get_snapshot_by_id(snapshot_id=snapshot_id, upload_dir=settings.upload_dir)
    file_path = resolve_snapshot_file_path(snapshot=snapshot, upload_dir=settings.upload_dir)

    media_type = "application/json" if snapshot.file_format == "json" else "text/csv"
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=snapshot.original_filename,
        content_disposition_type="attachment",
    )


@router.post(
    "/{snapshot_id}/parse",
    response_model=FileParseResponse,
    summary="Parse snapshot data",
    description="Parse dataset schema and records for a specific snapshot without modifying source bytes.",
)
@router.get(
    "/{snapshot_id}/parse",
    response_model=FileParseResponse,
    include_in_schema=False,
)
def parse_snapshot_endpoint(
    snapshot_id: str,
    settings: Settings = Depends(get_settings),
) -> FileParseResponse:
    """Parse specified snapshot file using deterministic parser."""
    snapshot = get_snapshot_by_id(snapshot_id=snapshot_id, upload_dir=settings.upload_dir)
    result = parse_assessment_file(
        filename=snapshot.stored_filename,
        upload_dir=settings.upload_dir,
    )
    return FileParseResponse(**result)

