"""API v1 Endpoints Router."""

from fastapi import APIRouter, Depends
from app.api.v1.activities import router as activities_router
from app.api.v1.enrichment_discovery import router as discovery_router
from app.api.v1.parser import router as parser_router
from app.api.v1.processing import router as processing_router
from app.api.v1.snapshots import router as snapshots_router
from app.api.v1.uploads import router as uploads_router
from app.config import Settings, get_settings
from app.models.schemas import HealthResponse

api_router = APIRouter(prefix="/v1")

# Mount sub-routers
api_router.include_router(activities_router)
api_router.include_router(uploads_router)
api_router.include_router(parser_router)
api_router.include_router(snapshots_router)
api_router.include_router(processing_router)
api_router.include_router(discovery_router)


@api_router.get("/health", response_model=HealthResponse, tags=["System"])
def get_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return system health status and runtime configuration."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.version,
        environment=settings.environment,
        mock_mode=settings.mock_mode,
    )

