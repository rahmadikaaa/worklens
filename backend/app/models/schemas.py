"""Domain and API Pydantic schemas for WORKLENS."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CalculationStatusEnum(str, Enum):
    """Deterministic calculation status priorities."""

    INVALID_INPUT = "INVALID_INPUT"
    MISSING_INPUT = "MISSING_INPUT"
    NEGATIVE_INPUT = "NEGATIVE_INPUT"
    ZERO_WORKLOAD = "ZERO_WORKLOAD"
    NEGATIVE_SAVINGS = "NEGATIVE_SAVINGS"
    CALCULATED = "CALCULATED"


class EvidenceStatusEnum(str, Enum):
    """Evidence status based on documentation links."""

    LINK_PROVIDED = "LINK_PROVIDED"
    NO_LINK_ATTACHED = "NO_LINK_ATTACHED"


class ChangeClassificationEnum(str, Enum):
    """Change detection classification."""

    UNCHANGED = "UNCHANGED"
    MODIFIED = "MODIFIED"
    ADDED = "ADDED"
    DELETED = "DELETED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class ChangeSummaryCounts(BaseModel):
    """Activity counts grouped by change classification."""

    total_current_rows: int = Field(0, description="Total current rows evaluated")
    unchanged: int = Field(0, description="Count of unchanged activities reused")
    modified: int = Field(0, description="Count of modified activities processed")
    added: int = Field(0, description="Count of new activities processed")
    deleted: int = Field(0, description="Count of deleted activities excluded from active dataset")
    review_required: int = Field(0, description="Count of activities requiring manual review")
    reprocess_count: int = Field(0, description="Count of activities re-evaluated (added + modified)")


class RowChangeItem(BaseModel):
    """Audit item for a single activity change classification."""

    activity_id: str
    source_row_index: Optional[int] = None
    classification: str
    content_hash: str
    previous_content_hash: Optional[str] = None
    reason: Optional[str] = None
    modified_fields: List[str] = Field(default_factory=list)


class ChangeReportResponse(BaseModel):
    """Change detection report comparing current snapshot against baseline."""

    status: str = Field(..., description="'NO_CHANGE' or 'CHANGES_DETECTED'")
    snapshot_id: str
    source_id: str
    baseline_snapshot_id: Optional[str] = None
    identical_content_hash: bool = False
    logic_version: str = "1.0.0"
    summary_counts: ChangeSummaryCounts
    changes: List[RowChangeItem] = Field(default_factory=list)
    reprocess_count: int = 0
    message: str


class IncrementalProcessResponse(BaseModel):
    """Response returned upon running incremental processing (P4)."""

    run_id: str
    snapshot_id: str
    source_id: str
    baseline_snapshot_id: Optional[str] = None
    status: str
    logic_version: str = "1.0.0"
    summary_counts: ChangeSummaryCounts
    total_active_records: int
    reprocessed_records: int
    reused_records: int
    change_report: ChangeReportResponse
    created_at: str


class RunSummaryItem(BaseModel):
    """Summary record for a historical processing run."""

    run_id: str
    snapshot_id: str
    source_id: str
    baseline_snapshot_id: Optional[str] = None
    status: str
    logic_version: str = "1.0.0"
    summary_counts: ChangeSummaryCounts
    total_active_records: int
    reprocessed_records: int
    reused_records: int
    created_at: str


class HealthResponse(BaseModel):
    """System health status response."""

    status: str = "ok"
    app_name: str
    version: str
    environment: str
    mock_mode: bool


class SummaryResponse(BaseModel):
    """High-level summary of processed workload dataset."""

    total_activities: int
    total_applications: int
    total_workload_initial_min: float
    total_workload_after_min: float
    total_workload_saved_min: float
    overall_reduction_pct: float
    evidence_provided_count: int
    calculation_breakdown: Dict[str, int]
    last_updated: Optional[str] = None


class ApplicationItem(BaseModel):
    """Summary item for an application workload profile."""

    application_name: str
    activity_count: int
    total_workload_min: float
    total_saved_min: float
    avg_reduction_pct: float


class AIFindingModel(BaseModel):
    """Qualitative review finding model."""

    finding_id: str
    source_row_index: int
    activity_ref: str
    application: str
    focus_area: str
    confidence_level: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str
    recommendation: str
    activity_id: Optional[str] = None
    action_by: Optional[str] = "L1"


class SourceSnapshot(BaseModel):
    """Metadata record for an uploaded source assessment snapshot (P3)."""

    snapshot_id: str = Field(..., description="Unique snapshot identifier")
    source_id: str = Field(..., description="Source identifier")
    original_filename: str = Field(..., description="Original filename uploaded by client")
    stored_filename: str = Field(..., description="Safe filename stored on disk")
    generated_at: Optional[str] = Field(None, description="ISO timestamp extracted from filename pattern")
    uploaded_at: str = Field(..., description="ISO timestamp of upload")
    file_format: str = Field(..., description="Detected file format ('json' or 'csv')")
    file_size: int = Field(..., description="File size in bytes")
    content_hash: str = Field(..., description="SHA-256 hex digest of file contents")
    status: str = Field("READY", description="Snapshot status (e.g. 'READY')")


class FileUploadResponse(BaseModel):
    """Response returned upon successful assessment file upload (P1)."""

    filename: str = Field(..., description="Original filename uploaded by client")
    saved_filename: str = Field(..., description="Safe filename stored on disk")
    file_format: str = Field(..., description="Detected file format ('json' or 'csv')")
    file_size: int = Field(..., description="Uploaded file size in bytes")
    upload_status: str = Field("success", description="Upload status")
    message: str = Field("File uploaded successfully", description="Status message")
    uploaded_at: Optional[str] = Field(None, description="ISO timestamp of upload")
    snapshot_id: Optional[str] = Field(None, description="Unique snapshot identifier")
    source_id: Optional[str] = Field(None, description="Source identifier")
    snapshot: Optional[SourceSnapshot] = Field(None, description="Full snapshot metadata")


class FileParseResponse(BaseModel):
    """Response returned upon parsing an uploaded assessment file (P2)."""

    filename: str = Field(..., description="Name of the parsed file")
    file_format: str = Field(..., description="Detected file format ('json' or 'csv')")
    total_rows: int = Field(..., description="Total count of data records")
    total_columns: int = Field(..., description="Total count of unique columns detected")
    columns: list[str] = Field(default_factory=list, description="List of detected column names")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary extracted from envelope")
    parsing_status: str = Field("success", description="Status of parsing operation")
    message: str = Field("File parsed successfully.", description="Status message")


class DatasetUploadResponse(BaseModel):
    """Response returned upon manual dataset upload and validation."""

    success: bool
    filename: str
    total_records: int
    valid_records: int
    validation_status: str
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

