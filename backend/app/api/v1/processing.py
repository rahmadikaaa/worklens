"""API endpoints for Change Detection & Incremental Processing (P4)."""

import json
from pathlib import Path
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.config import Settings, get_settings
from app.models.schemas import (
    ChangeReportResponse,
    IncrementalProcessResponse,
    RunSummaryItem,
)
from app.services.change_detection_service import (
    compare_snapshots,
    process_snapshot_incrementally,
)
from app.services.snapshot_service import get_snapshot_by_id

router = APIRouter(tags=["Change Detection & Incremental Processing"])


@router.post(
    "/snapshots/{snapshot_id}/compare",
    response_model=ChangeReportResponse,
    summary="Compare snapshot against baseline",
    description="Detect changes (UNCHANGED, MODIFIED, ADDED, DELETED, REVIEW_REQUIRED) against the preceding snapshot of the same source_id.",
)
def compare_snapshot_endpoint(
    snapshot_id: str,
    baseline_snapshot_id: Optional[str] = Query(None, description="Optional explicit baseline snapshot ID"),
    settings: Settings = Depends(get_settings),
) -> ChangeReportResponse:
    """Run change detection comparison without mutating any state."""
    current_snapshot = get_snapshot_by_id(snapshot_id, settings.upload_dir)
    report, _, _, _, _ = compare_snapshots(
        current_snapshot=current_snapshot,
        upload_dir=settings.upload_dir,
        storage_dir=settings.storage_dir,
        baseline_snapshot_id=baseline_snapshot_id,
    )
    return report


@router.post(
    "/snapshots/{snapshot_id}/process",
    response_model=IncrementalProcessResponse,
    summary="Execute incremental processing",
    description="Process only modified and added activities, reusing unchanged calculations and excluding deleted activities.",
)
def process_snapshot_endpoint(
    snapshot_id: str,
    baseline_snapshot_id: Optional[str] = Query(None, description="Optional explicit baseline snapshot ID"),
    settings: Settings = Depends(get_settings),
) -> IncrementalProcessResponse:
    """Execute change detection and incremental enrichment on specified snapshot."""
    return process_snapshot_incrementally(
        snapshot_id=snapshot_id,
        upload_dir=settings.upload_dir,
        storage_dir=settings.storage_dir,
        baseline_snapshot_id=baseline_snapshot_id,
    )


@router.get(
    "/snapshots/{snapshot_id}/change-report",
    response_model=ChangeReportResponse,
    summary="Get change report for snapshot",
    description="Retrieve change detection report comparing snapshot against its baseline.",
)
def get_snapshot_change_report_endpoint(
    snapshot_id: str,
    baseline_snapshot_id: Optional[str] = Query(None, description="Optional explicit baseline snapshot ID"),
    settings: Settings = Depends(get_settings),
) -> ChangeReportResponse:
    """Retrieve change detection report for snapshot."""
    current_snapshot = get_snapshot_by_id(snapshot_id, settings.upload_dir)
    report, _, _, _, _ = compare_snapshots(
        current_snapshot=current_snapshot,
        upload_dir=settings.upload_dir,
        storage_dir=settings.storage_dir,
        baseline_snapshot_id=baseline_snapshot_id,
    )
    return report


@router.get(
    "/runs",
    response_model=List[RunSummaryItem],
    summary="List all processing runs",
    description="Retrieve historical processing runs.",
)
def list_runs_endpoint(
    snapshot_id: Optional[str] = Query(None, description="Filter runs by snapshot ID"),
    source_id: Optional[str] = Query(None, description="Filter runs by source ID"),
    settings: Settings = Depends(get_settings),
) -> List[RunSummaryItem]:
    """List historical processing runs."""
    if not settings.storage_dir.exists():
        return []

    runs: List[RunSummaryItem] = []
    for run_dir in sorted(settings.storage_dir.glob("run_*"), reverse=True):
        if not run_dir.is_dir():
            continue
        meta_file = run_dir / "run_metadata.json"
        if meta_file.is_file():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                if snapshot_id and meta.get("snapshot_id") != snapshot_id:
                    continue
                if source_id and meta.get("source_id") != source_id:
                    continue
                runs.append(RunSummaryItem(**meta))
            except Exception:
                continue

    return runs


@router.get(
    "/runs/{run_id}",
    response_model=RunSummaryItem,
    summary="Get run metadata",
    description="Retrieve details for a specific processing run.",
)
def get_run_endpoint(
    run_id: str,
    settings: Settings = Depends(get_settings),
) -> RunSummaryItem:
    """Retrieve details for a specific processing run."""
    run_dir = (settings.storage_dir / run_id).resolve()
    try:
        run_dir.relative_to(settings.storage_dir.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid run ID.",
        )

    meta_file = run_dir / "run_metadata.json"
    if not meta_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run '{run_id}' not found.",
        )

    return RunSummaryItem(**json.loads(meta_file.read_text(encoding="utf-8")))
