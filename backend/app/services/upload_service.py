"""Service handling file upload validation and storage for WORKLENS."""

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Optional
from fastapi import HTTPException, UploadFile, status

# Allowed file extensions and corresponding MIME content types
ALLOWED_CONTENT_TYPES: dict[str, set[str]] = {
    "json": {
        "application/json",
        "text/json",
        "application/problem+json",
    },
    "csv": {
        "text/csv",
        "application/vnd.ms-excel",
        "text/plain",
        "application/csv",
    },
}

CHUNK_SIZE = 64 * 1024  # 64 KB chunk size for streaming


def sanitize_filename_stem(raw_stem: str) -> str:
    """Sanitize filename stem to prevent path traversal and unsafe characters."""
    sanitized = re.sub(r"[^a-zA-Z0-9_\-]", "_", raw_stem)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return sanitized if sanitized else "upload"


def get_collision_free_path(upload_dir: Path, safe_stem: str, suffix: str) -> tuple[Path, str]:
    """Find a non-colliding file path in the upload directory."""
    candidate_name = f"{safe_stem}{suffix}"
    candidate_path = upload_dir / candidate_name
    counter = 1

    while candidate_path.exists():
        candidate_name = f"{safe_stem}_{counter}{suffix}"
        candidate_path = upload_dir / candidate_name
        counter += 1

    return candidate_path, candidate_name


async def process_and_save_upload(
    file: UploadFile,
    upload_dir: Path,
    max_size_bytes: int,
    source_id: Optional[str] = None,
) -> dict:
    """Validate and safely persist an uploaded assessment file.

    Performs:
    1. Filename validation (presence and allowed extension .json/.csv).
    2. Content-type validation against allowed MIME types.
    3. Maximum file size and empty file verification.
    4. Safe filename sanitization and collision protection.
    5. Bit-for-bit exact binary preservation on disk.
    """
    raw_filename = file.filename or ""
    basename = Path(raw_filename).name.strip()
    if not basename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing or empty filename in upload request.",
        )

    suffix = Path(basename).suffix.lower()
    if suffix not in {".json", ".csv"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{suffix}'. Allowed extensions are: .json, .csv",
        )

    file_format = suffix.lstrip(".")
    allowed_mimes = ALLOWED_CONTENT_TYPES.get(file_format, set())

    # Extract base MIME type (ignoring optional params like ; charset=utf-8)
    raw_content_type = (file.content_type or "").split(";")[0].strip().lower()
    if raw_content_type not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid content type '{file.content_type}'. "
                f"Allowed content types for {file_format.upper()} files are: "
                f"{', '.join(sorted(allowed_mimes))}"
            ),
        )

    # Read chunks safely while enforcing max_size_bytes and streaming memory cap
    byte_chunks: list[bytes] = []
    total_bytes = 0

    while chunk := await file.read(CHUNK_SIZE):
        total_bytes += len(chunk)
        if total_bytes > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=(
                    f"File size exceeds maximum allowed limit of {max_size_bytes} bytes "
                    f"({max_size_bytes / (1024 * 1024):.1f} MB)."
                ),
            )
        byte_chunks.append(chunk)

    if total_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    raw_bytes = b"".join(byte_chunks)

    # Sanitize and resolve unique collision-free destination
    raw_stem = Path(basename).stem
    safe_stem = sanitize_filename_stem(raw_stem)

    upload_dir.mkdir(parents=True, exist_ok=True)
    target_path, saved_name = get_collision_free_path(upload_dir, safe_stem, suffix)

    try:
        with open(target_path, "wb") as destination:
            destination.write(raw_bytes)
            destination.flush()
    except OSError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file to disk: {err}",
        ) from err

    # Register immutable source snapshot (P3)
    from app.services.snapshot_service import create_source_snapshot

    snapshot = create_source_snapshot(
        upload_dir=upload_dir,
        original_filename=basename,
        stored_filename=saved_name,
        raw_bytes=raw_bytes,
        file_format=file_format,
        source_id=source_id,
    )

    return {
        "filename": basename,
        "saved_filename": saved_name,
        "file_format": file_format,
        "file_size": total_bytes,
        "upload_status": "success",
        "message": "File uploaded successfully.",
        "uploaded_at": snapshot.uploaded_at,
        "snapshot_id": snapshot.snapshot_id,
        "source_id": snapshot.source_id,
        "snapshot": snapshot,
    }
