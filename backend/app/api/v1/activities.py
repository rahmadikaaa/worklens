"""API router for querying, filtering, and inspecting enriched operational activities (V1)."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query
from app.config import Settings, get_settings
from app.services.activities_service import (
    get_single_activity,
    load_and_enrich_activities,
    query_activities,
)

router = APIRouter(prefix="/activities", tags=["Activities & Workload Exploration"])


@router.get(
    "/summary",
    summary="Get overall workload and activities summary",
    description="Returns high-level KPI metrics, criticality distribution, and automation progress without row data.",
)
def get_activities_summary_endpoint(
    filename: Optional[str] = Query(None, description="Optional filename, defaults to breakdown_activity_261106_1112.json"),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Return executive summary metrics and filter options for the dataset."""
    dataset = load_and_enrich_activities(filename=filename, upload_dir=settings.upload_dir)
    return {
        "summary": dataset["summary"],
        "filter_options": dataset["filter_options"],
    }


@router.get(
    "",
    summary="Query and filter enriched operational activities",
    description="Query activities with full-text search, multi-field filtering, sorting, and pagination.",
)
def query_activities_endpoint(
    filename: Optional[str] = Query(None, description="Optional filename, defaults to breakdown_activity_261106_1112.json"),
    search: Optional[str] = Query(None, description="Search term matching name, id, app, or SOP"),
    app: Optional[str] = Query(None, description="Filter by application name"),
    dept: Optional[str] = Query(None, description="Filter by department"),
    criticality: Optional[str] = Query(None, description="Filter by criticality (APP PRIORITY)"),
    assessment_status: Optional[str] = Query(None, description="Filter by assessment status"),
    calc_status: Optional[str] = Query(None, description="Filter by workload calculation status"),
    automation_status: Optional[str] = Query(None, description="Filter by automation status (Automation/Manual)"),
    category_action: Optional[str] = Query(None, description="Filter by category action"),
    bucket: Optional[str] = Query(None, description="Filter by opportunity bucket (Kandidat, Sudah diotomasi, etc.)"),
    tool: Optional[str] = Query(None, description="Filter by Tools Automation"),
    activity_type: Optional[str] = Query(None, description="Filter by TYPE ACTIVITY"),
    team: Optional[str] = Query(None, description="Filter by Team QC"),
    status_triggered: Optional[str] = Query(None, description="Filter by trigger status (Fully Automated, Not Yet Triggered, etc.)"),
    candidate_tech: Optional[str] = Query(None, description="Filter by recommended technology"),
    quick_win_only: Optional[bool] = Query(None, description="Filter quick-win candidates only"),
    outlier_only: Optional[bool] = Query(None, description="Filter extreme workload outliers only"),
    verified_baseline_only: Optional[bool] = Query(None, description="Filter verified baseline use cases only"),
    has_workload: Optional[bool] = Query(None, description="Filter only records with positive workload"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    sort_by: str = Query("activity_id", description="Field to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Execute dynamic query on operational dataset."""
    return query_activities(
        filename=filename,
        upload_dir=settings.upload_dir,
        search=search,
        app=app,
        dept=dept,
        criticality=criticality,
        assessment_status=assessment_status,
        calc_status=calc_status,
        automation_status=automation_status,
        category_action=category_action,
        bucket=bucket,
        tool=tool,
        activity_type=activity_type,
        team=team,
        status_triggered=status_triggered,
        candidate_tech=candidate_tech,
        quick_win_only=quick_win_only,
        outlier_only=outlier_only,
        verified_baseline_only=verified_baseline_only,
        has_workload=has_workload,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{activity_id:path}",
    summary="Get single activity full details",
    description="Retrieve all 37 source columns plus 6 derived metrics for an activity by its activity_id.",
)
def get_activity_detail_endpoint(
    activity_id: str,
    filename: Optional[str] = Query(None, description="Optional filename"),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Retrieve full activity details for the side drawer."""
    return get_single_activity(
        activity_id=activity_id,
        filename=filename,
        upload_dir=settings.upload_dir,
    )
