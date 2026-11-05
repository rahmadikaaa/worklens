"""API v1 Endpoints Router."""

from fastapi import APIRouter, Depends
from app.config import Settings, get_settings
from app.models.schemas import HealthResponse

api_router = APIRouter(prefix="/v1")


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
