"""Change Detection Engine Module for WORKLENS (Milestone 2).

Authoritative rules per PRD Section 5:
- activity_id is the primary unique identifier; never synthesized or composite.
- Deterministic SHA-256 row content hash across non-derived source columns.
- State classification: UNCHANGED, MODIFIED, ADDED, DELETED, REVIEW_REQUIRED.
- Anomaly reasons: EMPTY_ACTIVITY_ID, DUPLICATE_ACTIVITY_ID, AMBIGUOUS_MATCH.
- Exclude derived columns from hashing and delta comparisons.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple, Union

from app.core.enrichment import DERIVED_COLUMNS, DERIVED_COLUMN_ALIASES


class ChangeClassification(str, Enum):
    """Row change classification matching PRD Section 5.1."""

    UNCHANGED = "UNCHANGED"
    MODIFIED = "MODIFIED"
    ADDED = "ADDED"
    DELETED = "DELETED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class ReviewRequiredReason(str, Enum):
    """Reason enum for ambiguous or invalid row identity matching."""

    EMPTY_ACTIVITY_ID = "EMPTY_ACTIVITY_ID"
    DUPLICATE_ACTIVITY_ID = "DUPLICATE_ACTIVITY_ID"
    AMBIGUOUS_MATCH = "AMBIGUOUS_MATCH"


@dataclass(frozen=True)
class RowChangeRecord:
    """Audit record for a single row change classification."""

    activity_id: str
    source_row_index: Optional[int]
    classification: ChangeClassification
    content_hash: str
    previous_content_hash: Optional[str] = None
    reason: Optional[ReviewRequiredReason] = None
    modified_fields: Tuple[str, ...] = ()
    inherited_findings: Tuple[Dict[str, Any], ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to JSON-serializable dictionary."""
        result: Dict[str, Any] = {
            "activity_id": self.activity_id,
            "source_row_index": self.source_row_index,
            "classification": self.classification.value,
            "content_hash": self.content_hash,
        }
        if self.previous_content_hash is not None:
            result["previous_content_hash"] = self.previous_content_hash
        if self.reason is not None:
            result["reason"] = self.reason.value
        if self.modified_fields:
            result["modified_fields"] = list(self.modified_fields)
        if self.inherited_findings:
            result["inherited_findings"] = list(self.inherited_findings)
        return result


@dataclass(frozen=True)
class BaselineRecord:
    """Cached representation of a row from previous baseline snapshot."""

    activity_id: str
    source_row_index: Optional[int]
    content_hash: str
    source_data: Mapping[str, Any]
    enriched_data: Optional[Mapping[str, Any]] = None
    findings: Tuple[Dict[str, Any], ...] = ()


@dataclass(frozen=True)
class ChangeDetectionResult:
    """Comprehensive result of Change Detection comparison."""

    baseline_snapshot_id: Optional[str]
    records: Tuple[RowChangeRecord, ...]
    summary_counts: Dict[str, int]
    ai_queue: Tuple[Dict[str, Any], ...]

    @property
    def total_current_rows(self) -> int:
        """Total current rows evaluated (excluding deleted baseline rows)."""
        return sum(
            1 for r in self.records if r.classification != ChangeClassification.DELETED
        )

    @property
    def reprocess_count(self) -> int:
        """Count of rows requiring processing (ADDED + MODIFIED)."""
        return (
            self.summary_counts.get(ChangeClassification.ADDED.value, 0)
            + self.summary_counts.get(ChangeClassification.MODIFIED.value, 0)
        )


def is_derived_column(col_name: str) -> bool:
    """Check if column name represents a derived metric or internal metadata."""
    if col_name.startswith("_"):
        return True
    if col_name in DERIVED_COLUMNS:
        return True
    cleaned = (
        col_name.lower()
        .replace(" ", "")
        .replace("_", "")
        .replace(".", "")
        .replace("(", "")
        .replace(")", "")
        .replace("%", "")
    )
    return cleaned in DERIVED_COLUMN_ALIASES


def compute_row_content_hash(
    row_data: Mapping[str, Any],
    exclude_keys: Optional[Set[str]] = None,
) -> str:
    """Compute deterministic SHA-256 hash of row data across non-derived source columns.

    Sorts keys alphabetically and normalizes whitespace for exact determinism.
    """
    excluded = set(exclude_keys) if exclude_keys is not None else set()

    candidate_keys = sorted([
        k for k in row_data.keys()
        if k not in excluded and not is_derived_column(str(k))
    ])

    parts: List[str] = []
    for k in candidate_keys:
        val = row_data.get(k)
        cleaned_val = "" if val is None else str(val).strip()
        parts.append(f"{str(k).strip()}={cleaned_val}")

    payload = "\x1f".join(parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def detect_field_differences(
    current_data: Mapping[str, Any],
    baseline_data: Mapping[str, Any],
    exclude_keys: Optional[Set[str]] = None,
) -> Tuple[str, ...]:
    """Detect specific column names that differ between baseline and current rows."""
    excluded = set(exclude_keys) if exclude_keys is not None else set()

    all_keys = sorted([
        k for k in set(current_data.keys()).union(baseline_data.keys())
        if k not in excluded and not is_derived_column(str(k))
    ])

    diffs: List[str] = []
    for k in all_keys:
        v_curr = str(current_data.get(k, "")).strip() if current_data.get(k) is not None else ""
        v_base = str(baseline_data.get(k, "")).strip() if baseline_data.get(k) is not None else ""
        if v_curr != v_base:
            diffs.append(k)

    return tuple(diffs)


def find_activity_id_key(sample_row: Mapping[str, Any]) -> Optional[str]:
    """Find the column name corresponding to activity_id case-insensitively."""
    for k in sample_row.keys():
        if str(k).strip().lower().replace("_", "") == "activityid":
            return str(k)
    return None


def run_change_detection(
    current_rows: Sequence[Mapping[str, Any]],
    baseline_records: Optional[Dict[str, BaselineRecord]] = None,
    baseline_snapshot_id: Optional[str] = None,
    ambiguous_baseline_ids: Optional[Set[str]] = None,
) -> ChangeDetectionResult:
    """Execute M2 Change Detection between current dataset and baseline snapshot.

    Strict rules:
    - Only reads activity_id directly from source rows.
    - Does not generate, concatenate, or reconstruct activity_id.
    - Missing/blank activity_id -> REVIEW_REQUIRED (EMPTY_ACTIVITY_ID).
    - Duplicate activity_id within run -> REVIEW_REQUIRED (DUPLICATE_ACTIVITY_ID) for all occurrences.
    - Only MODIFIED and ADDED rows enter the reprocess/AI queue.
    - UNCHANGED rows inherit previous baseline calculations and findings.
    - DELETED rows recorded in change log, removed from active dataset.
    """
    b_records = dict(baseline_records) if baseline_records else {}
    b_ambiguous = set(ambiguous_baseline_ids) if ambiguous_baseline_ids else set()

    # Detect activity_id column name
    id_col_name: Optional[str] = None
    if current_rows:
        id_col_name = find_activity_id_key(current_rows[0])

    # Count occurrences of activity_id in current rows to identify duplicates
    id_counts: Dict[str, int] = {}
    for row_data in current_rows:
        raw_id = row_data.get(id_col_name) if id_col_name else None
        act_id = str(raw_id).strip() if raw_id is not None else ""
        if act_id:
            id_counts[act_id] = id_counts.get(act_id, 0) + 1

    records: List[RowChangeRecord] = []
    ai_queue: List[Dict[str, Any]] = []
    matched_baseline_ids: Set[str] = set()

    summary_counts: Dict[str, int] = {
        ChangeClassification.UNCHANGED.value: 0,
        ChangeClassification.MODIFIED.value: 0,
        ChangeClassification.ADDED.value: 0,
        ChangeClassification.DELETED.value: 0,
        ChangeClassification.REVIEW_REQUIRED.value: 0,
    }

    # Evaluate each current row
    for row_idx, row_data in enumerate(current_rows, start=1):
        raw_id = row_data.get(id_col_name) if id_col_name else None
        act_id = str(raw_id).strip() if raw_id is not None else ""
        content_hash = compute_row_content_hash(row_data)

        # Anomaly 1: Missing or Empty activity_id
        if not act_id:
            rec = RowChangeRecord(
                activity_id="",
                source_row_index=row_idx,
                classification=ChangeClassification.REVIEW_REQUIRED,
                content_hash=content_hash,
                reason=ReviewRequiredReason.EMPTY_ACTIVITY_ID,
            )
            records.append(rec)
            summary_counts[ChangeClassification.REVIEW_REQUIRED.value] += 1
            continue

        # Anomaly 2: Duplicate activity_id in active run
        if id_counts.get(act_id, 0) > 1:
            rec = RowChangeRecord(
                activity_id=act_id,
                source_row_index=row_idx,
                classification=ChangeClassification.REVIEW_REQUIRED,
                content_hash=content_hash,
                reason=ReviewRequiredReason.DUPLICATE_ACTIVITY_ID,
            )
            records.append(rec)
            summary_counts[ChangeClassification.REVIEW_REQUIRED.value] += 1
            continue

        # Anomaly 3: Ambiguous baseline identity
        if act_id in b_ambiguous:
            rec = RowChangeRecord(
                activity_id=act_id,
                source_row_index=row_idx,
                classification=ChangeClassification.REVIEW_REQUIRED,
                content_hash=content_hash,
                reason=ReviewRequiredReason.AMBIGUOUS_MATCH,
            )
            records.append(rec)
            summary_counts[ChangeClassification.REVIEW_REQUIRED.value] += 1
            continue

        # Compare with baseline
        if b_records and act_id in b_records:
            matched_baseline_ids.add(act_id)
            base_rec = b_records[act_id]

            if content_hash == base_rec.content_hash:
                rec = RowChangeRecord(
                    activity_id=act_id,
                    source_row_index=row_idx,
                    classification=ChangeClassification.UNCHANGED,
                    content_hash=content_hash,
                    previous_content_hash=base_rec.content_hash,
                    inherited_findings=base_rec.findings,
                )
                records.append(rec)
                summary_counts[ChangeClassification.UNCHANGED.value] += 1
            else:
                diff_fields = detect_field_differences(row_data, base_rec.source_data)
                rec = RowChangeRecord(
                    activity_id=act_id,
                    source_row_index=row_idx,
                    classification=ChangeClassification.MODIFIED,
                    content_hash=content_hash,
                    previous_content_hash=base_rec.content_hash,
                    modified_fields=diff_fields,
                )
                records.append(rec)
                summary_counts[ChangeClassification.MODIFIED.value] += 1
                ai_queue.append({
                    "activity_id": act_id,
                    "source_row_index": row_idx,
                    "change_classification": ChangeClassification.MODIFIED.value,
                    "modified_fields": list(diff_fields),
                    "source_data": dict(row_data),
                })
        else:
            rec = RowChangeRecord(
                activity_id=act_id,
                source_row_index=row_idx,
                classification=ChangeClassification.ADDED,
                content_hash=content_hash,
            )
            records.append(rec)
            summary_counts[ChangeClassification.ADDED.value] += 1
            ai_queue.append({
                "activity_id": act_id,
                "source_row_index": row_idx,
                "change_classification": ChangeClassification.ADDED.value,
                "modified_fields": [],
                "source_data": dict(row_data),
            })

    # Detect DELETED rows (present in baseline, absent in current valid rows)
    if b_records:
        for b_act_id, b_rec in b_records.items():
            if b_act_id not in matched_baseline_ids and b_act_id not in id_counts:
                del_rec = RowChangeRecord(
                    activity_id=b_act_id,
                    source_row_index=None,
                    classification=ChangeClassification.DELETED,
                    content_hash="",
                    previous_content_hash=b_rec.content_hash,
                )
                records.append(del_rec)
                summary_counts[ChangeClassification.DELETED.value] += 1

    return ChangeDetectionResult(
        baseline_snapshot_id=baseline_snapshot_id,
        records=tuple(records),
        summary_counts=summary_counts,
        ai_queue=tuple(ai_queue),
    )


def write_change_log(
    result: ChangeDetectionResult,
    target_path: Union[str, Path],
    current_run_id: str,
    timestamp: Optional[datetime] = None,
) -> Path:
    """Generate change_log.json according to approved specification."""
    path = Path(target_path)
    ts = timestamp if timestamp is not None else datetime.now(timezone.utc)

    log_data: Dict[str, Any] = {
        "run_id": current_run_id,
        "baseline_snapshot_id": result.baseline_snapshot_id,
        "generated_at_utc": ts.isoformat(),
        "summary_counts": {
            "total_current_rows": result.total_current_rows,
            "unchanged": result.summary_counts.get(ChangeClassification.UNCHANGED.value, 0),
            "modified": result.summary_counts.get(ChangeClassification.MODIFIED.value, 0),
            "added": result.summary_counts.get(ChangeClassification.ADDED.value, 0),
            "deleted": result.summary_counts.get(ChangeClassification.DELETED.value, 0),
            "review_required": result.summary_counts.get(
                ChangeClassification.REVIEW_REQUIRED.value, 0
            ),
            "reprocess_count": result.reprocess_count,
        },
        "changes": [r.to_dict() for r in result.records],
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode="w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)

    return path
