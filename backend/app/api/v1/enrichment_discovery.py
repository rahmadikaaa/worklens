"""API router for Enrichment Discovery & Reverse Engineering."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Query
from app.services.discovery_service import get_discovery_report

router = APIRouter(prefix="/enrichment", tags=["Enrichment Discovery"])


@router.get(
    "/discovery",
    summary="Get reverse engineering enrichment discovery results",
    description="Returns verified rules, decision tables, exception analysis, and validation metrics for the 667 benchmark records.",
)
def get_enrichment_discovery(
    json_path: Optional[str] = Query(None, description="Optional custom source JSON path"),
    csv_path: Optional[str] = Query(None, description="Optional custom benchmark CSV path"),
) -> Dict[str, Any]:
    """Retrieve full reverse engineering discovery report."""
    return get_discovery_report(custom_json_path=json_path, custom_csv_path=csv_path)

