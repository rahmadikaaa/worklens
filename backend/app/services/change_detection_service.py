"""Service for snapshot comparison, change detection, and incremental processing (P4).

Implements:
1. Baseline lookup by source_id.
2. Fast SHA-256 identical content bypass (skips parsing & row comparison).
3. Row-level change detection (UNCHANGED, MODIFIED, ADDED, DELETED, REVIEW_REQUIRED).
4. Incremental processing (reuses UNCHANGED results, enriches ADDED/MODIFIED, excludes DELETED, flags REVIEW_REQUIRED).
5. Immutable run storage (runs/run_YYYYMMDD_HHMMSS_xxx/) with logic version compatibility guard.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from fastapi import HTTPException, status
from app.core.change_detection import (
    BaselineRecord,
    ChangeClassification,
    ChangeDetectionResult,
    ReviewRequiredReason,
    compute_row_content_hash,
    find_activity_id_key,
    run_change_detection,
    write_change_log,
)
from app.core.enrichment import (
    COL_CALCULATION_STATUS,
    COL_VALIDATION_NOTES,
    CalculationStatus,
    evaluate_row_workload,
)
from app.models.schemas import (
    ChangeReportResponse,
    ChangeSummaryCounts,
    IncrementalProcessResponse,
    RowChangeItem,
    SourceSnapshot,
)
from app.services.parser_service import extract_records_from_file, validate_and_resolve_file
from app.services.snapshot_service import get_snapshot_by_id, list_snapshots

CURRENT_LOGIC_VERSION = "1.0.0"


def find_baseline_snapshot(
    current_snapshot: SourceSnapshot,
    upload_dir: Path,
    baseline_snapshot_id: Optional[str] = None,
) -> Optional[SourceSnapshot]:
    """Find the immediate preceding snapshot for the same source_id."""
    if baseline_snapshot_id:
        baseline = get_snapshot_by_id(baseline_snapshot_id, upload_dir)
        return baseline

    # Chronologically sort all snapshots for this source_id
    all_snapshots = list_snapshots(upload_dir=upload_dir, source_id=current_snapshot.source_id)

    # Filter out snapshots uploaded after or equal to the current snapshot
    candidates = [
        s for s in all_snapshots
        if s.snapshot_id != current_snapshot.snapshot_id and s.uploaded_at <= current_snapshot.uploaded_at
    ]

    return candidates[0] if candidates else None


def find_latest_run_for_snapshot(
    snapshot_id: str,
    storage_dir: Path,
) -> Optional[Path]:
    """Find the run directory for a given snapshot ID if previously processed."""
    if not storage_dir.exists():
        return None

    matching_runs: List[Tuple[str, Path]] = []
    for run_dir in storage_dir.glob("run_*"):
        if not run_dir.is_dir():
            continue
        meta_file = run_dir / "run_metadata.json"
        if meta_file.is_file():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                if meta.get("snapshot_id") == snapshot_id:
                    matching_runs.append((meta.get("created_at", ""), run_dir))
            except Exception:
                continue

    if not matching_runs:
        return None

    # Return latest run
    matching_runs.sort(key=lambda x: x[0], reverse=True)
    return matching_runs[0][1]


def load_baseline_records(
    baseline_snapshot: SourceSnapshot,
    upload_dir: Path,
    storage_dir: Path,
) -> Tuple[Dict[str, BaselineRecord], Set[str], Optional[str], Optional[Path]]:
    """Load baseline records, ambiguous duplicates, logic version, and latest run directory."""
    baseline_run_dir = find_latest_run_for_snapshot(baseline_snapshot.snapshot_id, storage_dir)
    baseline_logic_version: Optional[str] = None
    baseline_records: Dict[str, BaselineRecord] = {}
    ambiguous_duplicate_ids: Set[str] = set()

    # If previous run exists, load enriched dataset and logic version
    if baseline_run_dir:
        meta_file = baseline_run_dir / "run_metadata.json"
        if meta_file.is_file():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                baseline_logic_version = meta.get("logic_version")
            except Exception:
                baseline_logic_version = None

        dataset_file = baseline_run_dir / "enriched_dataset.json"
        if dataset_file.is_file():
            try:
                enriched_rows = json.loads(dataset_file.read_text(encoding="utf-8"))
                id_col = None
                if enriched_rows:
                    id_col = find_activity_id_key(enriched_rows[0])

                for idx, row in enumerate(enriched_rows, start=1):
                    act_id = str(row.get(id_col, "")).strip() if id_col else ""
                    if not act_id:
                        continue
                    if act_id in baseline_records:
                        ambiguous_duplicate_ids.add(act_id)
                        del baseline_records[act_id]
                        continue
                    elif act_id in ambiguous_duplicate_ids:
                        continue

                    content_hash = compute_row_content_hash(row)
                    baseline_records[act_id] = BaselineRecord(
                        activity_id=act_id,
                        source_row_index=idx,
                        content_hash=content_hash,
                        source_data=row,
                        enriched_data=row,
                    )
                return baseline_records, ambiguous_duplicate_ids, baseline_logic_version, baseline_run_dir
            except Exception:
                pass

    # Fallback: load directly from the baseline raw snapshot file
    target_path = validate_and_resolve_file(baseline_snapshot.stored_filename, upload_dir)
    records, _, _ = extract_records_from_file(target_path)
    id_col = find_activity_id_key(records[0]) if records else None

    for idx, row in enumerate(records, start=1):
        act_id = str(row.get(id_col, "")).strip() if id_col else ""
        if not act_id:
            continue
        if act_id in baseline_records:
            ambiguous_duplicate_ids.add(act_id)
            del baseline_records[act_id]
            continue
        elif act_id in ambiguous_duplicate_ids:
            continue

        content_hash = compute_row_content_hash(row)
        baseline_records[act_id] = BaselineRecord(
            activity_id=act_id,
            source_row_index=idx,
            content_hash=content_hash,
            source_data=row,
            enriched_data=None,
        )

    return baseline_records, ambiguous_duplicate_ids, baseline_logic_version, None


def compare_snapshots(
    current_snapshot: SourceSnapshot,
    upload_dir: Path,
    storage_dir: Path,
    baseline_snapshot_id: Optional[str] = None,
) -> Tuple[ChangeReportResponse, Optional[ChangeDetectionResult], Optional[List[Dict[str, Any]]], Optional[Dict[str, BaselineRecord]], Optional[str]]:
    """Compare current snapshot against its baseline snapshot."""
    baseline = find_baseline_snapshot(
        current_snapshot=current_snapshot,
        upload_dir=upload_dir,
        baseline_snapshot_id=baseline_snapshot_id,
    )

    # 1. Fast Path: Identical content hash check (Byte-for-byte identical)
    if baseline and current_snapshot.content_hash == baseline.content_hash:
        # Load count of records without full row comparison
        target_path = validate_and_resolve_file(current_snapshot.stored_filename, upload_dir)
        records, _, _ = extract_records_from_file(target_path)
        total_rows = len(records)

        summary = ChangeSummaryCounts(
            total_current_rows=total_rows,
            unchanged=total_rows,
            modified=0,
            added=0,
            deleted=0,
            review_required=0,
            reprocess_count=0,
        )

        report = ChangeReportResponse(
            status="NO_CHANGE",
            snapshot_id=current_snapshot.snapshot_id,
            source_id=current_snapshot.source_id,
            baseline_snapshot_id=baseline.snapshot_id,
            identical_content_hash=True,
            logic_version=CURRENT_LOGIC_VERSION,
            summary_counts=summary,
            changes=[],
            reprocess_count=0,
            message="Snapshots are byte-for-byte identical (matching SHA-256). Data comparison skipped; previous results retained.",
        )
        return report, None, records, None, CURRENT_LOGIC_VERSION

    # 2. Extract current rows
    target_path = validate_and_resolve_file(current_snapshot.stored_filename, upload_dir)
    current_rows, _, _ = extract_records_from_file(target_path)

    # 3. Load baseline data if baseline snapshot exists
    baseline_records: Dict[str, BaselineRecord] = {}
    ambiguous_ids: Set[str] = set()
    b_id: Optional[str] = None
    baseline_logic_version: Optional[str] = None

    if baseline:
        b_id = baseline.snapshot_id
        baseline_records, ambiguous_ids, baseline_logic_version, _ = load_baseline_records(
            baseline_snapshot=baseline,
            upload_dir=upload_dir,
            storage_dir=storage_dir,
        )

    # 4. Run deterministic change detection
    result = run_change_detection(
        current_rows=current_rows,
        baseline_records=baseline_records,
        baseline_snapshot_id=b_id,
        ambiguous_baseline_ids=ambiguous_ids,
    )

    # 5. Check if all rows are UNCHANGED (same data content, different file bytes)
    is_all_unchanged = (
        baseline is not None
        and result.summary_counts[ChangeClassification.MODIFIED.value] == 0
        and result.summary_counts[ChangeClassification.ADDED.value] == 0
        and result.summary_counts[ChangeClassification.DELETED.value] == 0
        and result.summary_counts[ChangeClassification.REVIEW_REQUIRED.value] == 0
        and result.summary_counts[ChangeClassification.UNCHANGED.value] == len(current_rows)
    )

    status_str = "NO_CHANGE" if is_all_unchanged else "CHANGES_DETECTED"
    msg = (
        "Dataset content is identical to baseline. Enrichment and AI assessment skipped."
        if is_all_unchanged
        else f"Change detection completed: {result.reprocess_count} activities need processing."
    )

    change_items = [
        RowChangeItem(
            activity_id=r.activity_id,
            source_row_index=r.source_row_index,
            classification=r.classification.value,
            content_hash=r.content_hash,
            previous_content_hash=r.previous_content_hash,
            reason=r.reason.value if r.reason else None,
            modified_fields=list(r.modified_fields),
        )
        for r in result.records
    ]

    summary = ChangeSummaryCounts(
        total_current_rows=result.total_current_rows,
        unchanged=result.summary_counts.get(ChangeClassification.UNCHANGED.value, 0),
        modified=result.summary_counts.get(ChangeClassification.MODIFIED.value, 0),
        added=result.summary_counts.get(ChangeClassification.ADDED.value, 0),
        deleted=result.summary_counts.get(ChangeClassification.DELETED.value, 0),
        review_required=result.summary_counts.get(ChangeClassification.REVIEW_REQUIRED.value, 0),
        reprocess_count=result.reprocess_count,
    )

    report = ChangeReportResponse(
        status=status_str,
        snapshot_id=current_snapshot.snapshot_id,
        source_id=current_snapshot.source_id,
        baseline_snapshot_id=b_id,
        identical_content_hash=False,
        logic_version=CURRENT_LOGIC_VERSION,
        summary_counts=summary,
        changes=change_items,
        reprocess_count=result.reprocess_count,
        message=msg,
    )

    return report, result, current_rows, baseline_records, baseline_logic_version


def process_snapshot_incrementally(
    snapshot_id: str,
    upload_dir: Path,
    storage_dir: Path,
    baseline_snapshot_id: Optional[str] = None,
) -> IncrementalProcessResponse:
    """Execute change detection and incremental processing for a given snapshot."""
    current_snapshot = get_snapshot_by_id(snapshot_id, upload_dir)

    report, change_result, current_rows, baseline_records, baseline_logic_version = compare_snapshots(
        current_snapshot=current_snapshot,
        upload_dir=upload_dir,
        storage_dir=storage_dir,
        baseline_snapshot_id=baseline_snapshot_id,
    )

    now_utc = datetime.now(timezone.utc)
    run_id = f"run_{now_utc.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    run_dir = storage_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        active_enriched_records: List[Dict[str, Any]] = []
        reprocessed_count = 0
        reused_count = 0

        # Check logic version compatibility: only reuse calculations if versions match exactly
        is_logic_compatible = (
            baseline_logic_version is not None
            and baseline_logic_version == CURRENT_LOGIC_VERSION
        )

        if report.status == "NO_CHANGE":
            if is_logic_compatible:
                # Retain baseline results directly when logic versions match
                if baseline_records:
                    for b_rec in baseline_records.values():
                        if b_rec.enriched_data:
                            active_enriched_records.append(dict(b_rec.enriched_data))
                            reused_count += 1
                        else:
                            enriched = evaluate_row_workload(b_rec.source_data)
                            active_enriched_records.append(enriched.to_dict())
                            reprocessed_count += 1
                elif current_rows:
                    for idx, row in enumerate(current_rows, start=1):
                        enriched = evaluate_row_workload(row, source_row_index=idx)
                        active_enriched_records.append(enriched.to_dict())
                        reused_count += 1
            else:
                # Incompatible logic version: must re-evaluate all rows with current logic
                rows_to_process = current_rows or ([b.source_data for b in baseline_records.values()] if baseline_records else [])
                for idx, row in enumerate(rows_to_process, start=1):
                    enriched = evaluate_row_workload(row, source_row_index=idx)
                    active_enriched_records.append(enriched.to_dict())
                    reprocessed_count += 1

            # Write change log and metadata for NO_CHANGE run
            change_log_data = {
                "run_id": run_id,
                "snapshot_id": current_snapshot.snapshot_id,
                "baseline_snapshot_id": report.baseline_snapshot_id,
                "status": "NO_CHANGE",
                "generated_at_utc": now_utc.isoformat(),
                "summary_counts": report.summary_counts.model_dump(),
                "changes": [],
            }
            with open(run_dir / "change_log.json", "w", encoding="utf-8") as f:
                json.dump(change_log_data, f, indent=2)

        else:
            assert change_result is not None
            assert current_rows is not None

            # Index classified records by activity_id and source_row_index
            record_by_index: Dict[int, Any] = {}
            for rec in change_result.records:
                if rec.source_row_index is not None:
                    record_by_index[rec.source_row_index] = rec

            # Process rows incrementally
            for row_idx, row_data in enumerate(current_rows, start=1):
                change_rec = record_by_index.get(row_idx)
                classification = change_rec.classification if change_rec else ChangeClassification.ADDED

                if classification in (ChangeClassification.ADDED, ChangeClassification.MODIFIED):
                    # Process: Deterministic M1 Enrichment
                    enriched = evaluate_row_workload(row_data, source_row_index=row_idx)
                    enriched_dict = enriched.to_dict()
                    enriched_dict["_change_classification"] = classification.value
                    active_enriched_records.append(enriched_dict)
                    reprocessed_count += 1

                elif classification == ChangeClassification.UNCHANGED:
                    # Reuse previous calculations if logic compatible and available
                    b_rec = baseline_records.get(change_rec.activity_id) if baseline_records and change_rec else None
                    if is_logic_compatible and b_rec and b_rec.enriched_data:
                        reused_dict = dict(b_rec.enriched_data)
                        reused_dict["_change_classification"] = ChangeClassification.UNCHANGED.value
                        active_enriched_records.append(reused_dict)
                        reused_count += 1
                    else:
                        # Re-enrich due to logic incompatibility or missing cache
                        enriched = evaluate_row_workload(row_data, source_row_index=row_idx)
                        enriched_dict = enriched.to_dict()
                        enriched_dict["_change_classification"] = ChangeClassification.UNCHANGED.value
                        active_enriched_records.append(enriched_dict)
                        reprocessed_count += 1

                elif classification == ChangeClassification.REVIEW_REQUIRED:
                    # Flag for review: Do not auto-calculate valid metrics or reuse old results
                    raw_dict = dict(row_data)
                    raw_dict[COL_CALCULATION_STATUS] = CalculationStatus.INVALID_INPUT.value
                    raw_dict[COL_VALIDATION_NOTES] = f"REVIEW_REQUIRED: {change_rec.reason.value if change_rec and change_rec.reason else 'Unspecified issue'}"
                    raw_dict["_change_classification"] = ChangeClassification.REVIEW_REQUIRED.value
                    active_enriched_records.append(raw_dict)

                # DELETED rows are excluded from active_enriched_records!

            # Write change_log.json
            write_change_log(
                result=change_result,
                target_path=run_dir / "change_log.json",
                current_run_id=run_id,
                timestamp=now_utc,
            )

        # Write active enriched dataset
        with open(run_dir / "enriched_dataset.json", "w", encoding="utf-8") as f:
            json.dump(active_enriched_records, f, indent=2)

        # Write run metadata
        run_meta = {
            "run_id": run_id,
            "snapshot_id": current_snapshot.snapshot_id,
            "source_id": current_snapshot.source_id,
            "baseline_snapshot_id": report.baseline_snapshot_id,
            "status": report.status,
            "logic_version": CURRENT_LOGIC_VERSION,
            "summary_counts": report.summary_counts.model_dump(),
            "total_active_records": len(active_enriched_records),
            "reprocessed_records": reprocessed_count,
            "reused_records": reused_count,
            "created_at": now_utc.isoformat(),
        }
        with open(run_dir / "run_metadata.json", "w", encoding="utf-8") as f:
            json.dump(run_meta, f, indent=2)

        return IncrementalProcessResponse(
            run_id=run_id,
            snapshot_id=current_snapshot.snapshot_id,
            source_id=current_snapshot.source_id,
            baseline_snapshot_id=report.baseline_snapshot_id,
            status=report.status,
            logic_version=CURRENT_LOGIC_VERSION,
            summary_counts=report.summary_counts,
            total_active_records=len(active_enriched_records),
            reprocessed_records=reprocessed_count,
            reused_records=reused_count,
            change_report=report,
            created_at=now_utc.isoformat(),
        )

    except Exception as err:
        # Data integrity protection: never leave broken run directory
        if run_dir.exists():
            shutil.rmtree(run_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Incremental processing failed: {err}",
        ) from err
