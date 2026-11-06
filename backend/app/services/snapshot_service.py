"""Service for managing source snapshots, versioning, and history (P3)."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Optional
import uuid
from fastapi import HTTPException, status
from app.models.schemas import SourceSnapshot
from app.services.parser_service import validate_and_resolve_file
from app.services.upload_service import sanitize_filename_stem

SNAPSHOT_DIR_NAME = ".snapshots"

# Regex pattern for breakdown_activity_MMDD_HHMM.json
BREAKDOWN_PATTERN = re.compile(
    r"^breakdown_activity_(\d{2})(\d{2})_(\d{2})(\d{2})\.json$",
    re.IGNORECASE,
)

SNAPSHOT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]+$")


def extract_generated_at(filename: str) -> Optional[str]:
    """Extract generated_at ISO timestamp from filename pattern 'breakdown_activity_MMDD_HHMM.json'.

    If filename does not match the exact pattern or contains invalid date/time parts,
    returns None without failing the upload.
    """
    match = BREAKDOWN_PATTERN.match(filename)
    if not match:
        return None

    month_str, day_str, hour_str, min_str = match.groups()
    current_year = datetime.now(timezone.utc).year

    try:
        month = int(month_str)
        day = int(day_str)
        hour = int(hour_str)
        minute = int(min_str)
        dt = datetime(current_year, month, day, hour, minute, tzinfo=timezone.utc)
        return dt.isoformat()
    except ValueError:
        return None


def compute_content_hash(raw_bytes: bytes) -> str:
    """Compute deterministic SHA-256 hex digest of raw file bytes."""
    return hashlib.sha256(raw_bytes).hexdigest()


def get_snapshot_storage_dir(upload_dir: Path) -> Path:
    """Resolve and create isolated snapshot metadata directory inside upload directory."""
    meta_dir = upload_dir / SNAPSHOT_DIR_NAME
    meta_dir.mkdir(parents=True, exist_ok=True)
    return meta_dir


def create_source_snapshot(
    upload_dir: Path,
    original_filename: str,
    stored_filename: str,
    raw_bytes: bytes,
    file_format: str,
    source_id: Optional[str] = None,
) -> SourceSnapshot:
    """Create and persist an immutable metadata record for an uploaded source dataset."""
    now_utc = datetime.now(timezone.utc)
    uploaded_at_iso = now_utc.isoformat()
    timestamp_prefix = now_utc.strftime("%Y%m%d_%H%M%S")
    unique_suffix = uuid.uuid4().hex[:8]
    snapshot_id = f"snap_{timestamp_prefix}_{unique_suffix}"

    # Determine logical source identity
    if not source_id:
        if BREAKDOWN_PATTERN.match(original_filename) or original_filename.lower().startswith("breakdown_activity"):
            resolved_source_id = "breakdown_activity"
        else:
            resolved_source_id = sanitize_filename_stem(Path(original_filename).stem)
    else:
        resolved_source_id = sanitize_filename_stem(source_id)

    generated_at = extract_generated_at(original_filename)
    content_hash = compute_content_hash(raw_bytes)

    snapshot = SourceSnapshot(
        snapshot_id=snapshot_id,
        source_id=resolved_source_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        generated_at=generated_at,
        uploaded_at=uploaded_at_iso,
        file_format=file_format,
        file_size=len(raw_bytes),
        content_hash=content_hash,
        status="READY",
    )

    # Persist snapshot metadata to separate JSON file (immutable)
    meta_dir = get_snapshot_storage_dir(upload_dir)
    snapshot_meta_file = meta_dir / f"{snapshot_id}.json"

    try:
        with open(snapshot_meta_file, "w", encoding="utf-8") as f:
            f.write(snapshot.model_dump_json(indent=2))
            f.flush()
    except OSError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist snapshot metadata: {err}",
        ) from err

    return snapshot


def list_snapshots(upload_dir: Path, source_id: Optional[str] = None) -> list[SourceSnapshot]:
    """Retrieve all registered snapshots ordered chronologically (newest first)."""
    meta_dir = upload_dir / SNAPSHOT_DIR_NAME
    if not meta_dir.exists():
        return []

    snapshots: list[SourceSnapshot] = []
    for meta_file in meta_dir.glob("*.json"):
        if not meta_file.is_file():
            continue
        try:
            raw_text = meta_file.read_text(encoding="utf-8")
            data = json.loads(raw_text)
            snapshot = SourceSnapshot(**data)
            if source_id and snapshot.source_id != source_id:
                continue
            snapshots.append(snapshot)
        except (json.JSONDecodeError, ValueError, OSError):
            # Skip corrupted metadata records safely
            continue

    # Sort descending by uploaded_at, then snapshot_id
    snapshots.sort(key=lambda s: (s.uploaded_at, s.snapshot_id), reverse=True)
    return snapshots


def get_snapshot_by_id(snapshot_id: str, upload_dir: Path) -> SourceSnapshot:
    """Retrieve metadata for a specific snapshot by ID with path traversal protection."""
    if not snapshot_id or not SNAPSHOT_ID_PATTERN.match(snapshot_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid snapshot identifier format.",
        )

    meta_dir = upload_dir / SNAPSHOT_DIR_NAME
    meta_dir_resolved = meta_dir.resolve()
    target_meta_file = (meta_dir / f"{snapshot_id}.json").resolve()

    try:
        target_meta_file.relative_to(meta_dir_resolved)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid snapshot identifier: directory traversal detected.",
        )

    if not target_meta_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot '{snapshot_id}' not found.",
        )

    try:
        raw_text = target_meta_file.read_text(encoding="utf-8")
        data = json.loads(raw_text)
        return SourceSnapshot(**data)
    except (json.JSONDecodeError, ValueError) as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Snapshot metadata file is corrupted: {err}",
        ) from err


def resolve_snapshot_file_path(snapshot: SourceSnapshot, upload_dir: Path) -> Path:
    """Resolve physical path of snapshot data file ensuring source immutability."""
    return validate_and_resolve_file(snapshot.stored_filename, upload_dir)

