"""Deterministic Workload Enrichment Engine (Milestone 1).

Authoritative rules per PRD Section 4:
- Workload Saved = Workload - Workload after
- Workload Reduction % = ((Workload - Workload after) / Workload) * 100.0 (only when Workload > 0)
- Annualized Saved = Workload Saved * 12.0
- Strict 6-tier priority: INVALID_INPUT -> MISSING_INPUT -> NEGATIVE_INPUT -> ZERO_WORKLOAD -> NEGATIVE_SAVINGS -> CALCULATED
- Evidence status: LINK_PROVIDED vs NO_LINK_ATTACHED
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

# Standard derived column names
COL_WORKLOAD_SAVED = "Workload Saved Est. (Min/Month)"
COL_WORKLOAD_REDUCTION = "Workload Reduction Est. (%)"
COL_CALCULATION_STATUS = "Workload Calculation Status"
COL_EVIDENCE_STATUS = "Workload Evidence Status"
COL_VALIDATION_NOTES = "Workload Validation Notes"
COL_ANNUALIZED_SAVED = "Annualized Workload Saved Est. (Min/Year)"

DERIVED_COLUMNS: Tuple[str, ...] = (
    COL_WORKLOAD_SAVED,
    COL_WORKLOAD_REDUCTION,
    COL_CALCULATION_STATUS,
    COL_EVIDENCE_STATUS,
    COL_VALIDATION_NOTES,
    COL_ANNUALIZED_SAVED,
)

# Standard alias set for matching keys regardless of casing/spacing
DERIVED_COLUMN_ALIASES: set[str] = {
    c.lower().replace(" ", "").replace("_", "").replace(".", "").replace("(", "").replace(")", "").replace("%", "")
    for c in DERIVED_COLUMNS
}
DERIVED_COLUMN_ALIASES.update({
    "workloadsaved",
    "workloadsavedest",
    "workloadreduction",
    "workloadreductionpct",
    "workloadreductionest",
    "workloadcalculationstatus",
    "workloadevidencestatus",
    "workloadvalidationnotes",
    "annualizedsaved",
    "annualizedworkloadsavedest",
})


class CalculationStatus(str, Enum):
    """Deterministic calculation status priority hierarchy."""

    INVALID_INPUT = "INVALID_INPUT"
    MISSING_INPUT = "MISSING_INPUT"
    NEGATIVE_INPUT = "NEGATIVE_INPUT"
    ZERO_WORKLOAD = "ZERO_WORKLOAD"
    NEGATIVE_SAVINGS = "NEGATIVE_SAVINGS"
    CALCULATED = "CALCULATED"


class EvidenceStatus(str, Enum):
    """Evidence status reflecting documentation links."""

    LINK_PROVIDED = "LINK_PROVIDED"
    NO_LINK_ATTACHED = "NO_LINK_ATTACHED"


@dataclass(frozen=True)
class EnrichedRow:
    """Represents a single assessment row enriched with deterministic metrics."""

    source_row_index: int
    source_data: Mapping[str, Any]
    workload_saved: Optional[float]
    workload_reduction_pct: Optional[float]
    calculation_status: CalculationStatus
    evidence_status: EvidenceStatus
    validation_notes: str
    annualized_saved: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert enriched row to a dict retaining all source fields plus 6 derived fields."""
        result: Dict[str, Any] = dict(self.source_data)
        result[COL_WORKLOAD_SAVED] = (
            "" if self.workload_saved is None else self.workload_saved
        )
        result[COL_WORKLOAD_REDUCTION] = (
            "" if self.workload_reduction_pct is None else self.workload_reduction_pct
        )
        result[COL_CALCULATION_STATUS] = self.calculation_status.value
        result[COL_EVIDENCE_STATUS] = self.evidence_status.value
        result[COL_VALIDATION_NOTES] = self.validation_notes
        result[COL_ANNUALIZED_SAVED] = (
            "" if self.annualized_saved is None else self.annualized_saved
        )
        return result


def parse_numeric_field(raw_value: Optional[Any]) -> Tuple[Optional[float], Optional[str]]:
    """Parse numeric input safely without treating empty/whitespace as zero."""
    if raw_value is None:
        return None, "MISSING"

    cleaned = str(raw_value).strip()
    if cleaned == "":
        return None, "MISSING"

    try:
        val = float(cleaned)
        return val, None
    except ValueError:
        return None, "INVALID"


def get_field_case_insensitive(row: Mapping[str, Any], candidate_keys: Sequence[str]) -> Optional[Any]:
    """Retrieve field value case-insensitively and whitespace-insensitively."""
    # Direct lookup first
    for k in candidate_keys:
        if k in row:
            return row[k]

    # Normalized lookup
    normalized_map = {
        str(k).strip().lower().replace("_", " "): v for k, v in row.items()
    }
    for k in candidate_keys:
        norm_k = k.strip().lower().replace("_", " ")
        if norm_k in normalized_map:
            return normalized_map[norm_k]

    return None


def evaluate_row_workload(
    row: Mapping[str, Any],
    source_row_index: int = 1,
) -> EnrichedRow:
    """Evaluate and calculate deterministic workload metrics for a single assessment row.

    Strictly enforces 6-tier priority hierarchy using full native float precision.
    """
    raw_workload = get_field_case_insensitive(row, ["Workload", "workload", "initial_workload", "Workload (Min/Month)"])
    raw_workload_after = get_field_case_insensitive(row, ["Workload after", "workload_after", "Workload After", "Workload After (Min/Month)"])

    w_val, w_err = parse_numeric_field(raw_workload)
    wa_val, wa_err = parse_numeric_field(raw_workload_after)

    # Priority 1: INVALID_INPUT
    if w_err == "INVALID" or wa_err == "INVALID":
        calc_status = CalculationStatus.INVALID_INPUT
        saved = None
        reduction_pct = None
        annualized = None
        if w_err == "INVALID" and wa_err == "INVALID":
            notes = f"Invalid numeric format on Workload ({raw_workload!r}) and Workload after ({raw_workload_after!r})"
        elif w_err == "INVALID":
            notes = f"Invalid numeric format on Workload: {raw_workload!r}"
        else:
            notes = f"Invalid numeric format on Workload after: {raw_workload_after!r}"

    # Priority 2: MISSING_INPUT
    elif w_err == "MISSING" or wa_err == "MISSING":
        calc_status = CalculationStatus.MISSING_INPUT
        saved = None
        reduction_pct = None
        annualized = None
        if w_err == "MISSING" and wa_err == "MISSING":
            notes = "Missing value on Workload and Workload after"
        elif w_err == "MISSING":
            notes = "Missing value on Workload"
        else:
            notes = "Missing value on Workload after"

    # Priority 3: NEGATIVE_INPUT
    elif (w_val is not None and w_val < 0) or (wa_val is not None and wa_val < 0):
        calc_status = CalculationStatus.NEGATIVE_INPUT
        saved = (w_val or 0.0) - (wa_val or 0.0)
        reduction_pct = None
        annualized = saved * 12.0
        if w_val is not None and w_val < 0 and wa_val is not None and wa_val < 0:
            notes = f"Negative duration on Workload ({w_val}) and Workload after ({wa_val})"
        elif w_val is not None and w_val < 0:
            notes = f"Negative duration on Workload ({w_val})"
        else:
            notes = f"Negative duration on Workload after ({wa_val})"

    # Priority 4: ZERO_WORKLOAD
    elif w_val == 0.0:
        calc_status = CalculationStatus.ZERO_WORKLOAD
        saved = 0.0 - (wa_val or 0.0)
        reduction_pct = None
        annualized = saved * 12.0
        notes = "Initial workload is 0; percentage reduction undefined"

    # Priority 5: NEGATIVE_SAVINGS
    elif wa_val is not None and w_val is not None and wa_val > w_val:
        calc_status = CalculationStatus.NEGATIVE_SAVINGS
        saved = w_val - wa_val
        reduction_pct = ((w_val - wa_val) / w_val) * 100.0
        annualized = saved * 12.0
        notes = f"Workload after ({wa_val}) exceeds Workload ({w_val})"

    # Priority 6: CALCULATED
    else:
        assert w_val is not None and wa_val is not None
        calc_status = CalculationStatus.CALCULATED
        saved = w_val - wa_val
        reduction_pct = ((w_val - wa_val) / w_val) * 100.0
        annualized = saved * 12.0
        notes = ""

    # Evaluate Evidence Status
    link_conf = get_field_case_insensitive(row, ["Link Confluence", "link_confluence", "Link_Confluence", "link_conf"])
    link_wiki = get_field_case_insensitive(row, ["Link Wiki", "link_wiki", "Link_Wiki"])
    has_conf = bool(link_conf and str(link_conf).strip())
    has_wiki = bool(link_wiki and str(link_wiki).strip())

    if has_conf or has_wiki:
        evidence_status = EvidenceStatus.LINK_PROVIDED
    else:
        evidence_status = EvidenceStatus.NO_LINK_ATTACHED

    return EnrichedRow(
        source_row_index=source_row_index,
        source_data=row,
        workload_saved=saved,
        workload_reduction_pct=reduction_pct,
        calculation_status=calc_status,
        evidence_status=evidence_status,
        validation_notes=notes,
        annualized_saved=annualized,
    )

