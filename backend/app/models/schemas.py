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


class DatasetUploadResponse(BaseModel):
    """Response returned upon manual dataset upload and validation."""

    success: bool
    filename: str
    total_records: int
    valid_records: int
    validation_status: str
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
