"""WORKLENS FastAPI Application Entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.config import get_settings


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Unified Workload Intelligence Platform API",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Enable CORS for frontend integration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API routers
    application.include_router(api_router, prefix="/api")

    return application


app = create_application()


@app.get("/", tags=["Root"])
def root():
    """Root endpoint welcoming clients."""
    settings = get_settings()
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }

