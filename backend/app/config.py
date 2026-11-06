"""WORKLENS Backend Configuration."""

from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable override support."""

    app_name: str = "WORKLENS Workload Intelligence Platform"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # AI Reviewer
    mock_mode: bool = True
    ai_model: str = "gemini-1.5-flash"
    gemini_api_key: Optional[str] = None

    # Storage & Uploads
    storage_dir: Path = Path("runs")
    upload_dir: Path = Path("uploads")
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB default (configurable via WORKLENS_MAX_UPLOAD_SIZE_BYTES)

    # MCP Integration
    mcp_server_name: str = "worklens-enrichment"

    model_config = SettingsConfigDict(
        env_prefix="WORKLENS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()

