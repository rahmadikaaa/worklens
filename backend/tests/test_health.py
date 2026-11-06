"""Initial Smoke & Health Tests for WORKLENS Backend."""

from fastapi.testclient import TestClient
from app.config import Settings, get_settings
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify that root endpoint responds with basic info and documentation link."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "WORKLENS" in data["message"]
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/docs"


def test_health_endpoint():
    """Verify health endpoint returns status, environment, and mock mode flag."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "WORKLENS" in data["app_name"]
    assert data["mock_mode"] is True
    assert data["environment"] == "development"


def test_custom_settings_override():
    """Ensure settings can be overridden dynamically."""
    custom_settings = Settings(
        app_name="Custom WORKLENS Test",
        environment="testing",
        mock_mode=False,
    )
    app.dependency_overrides[get_settings] = lambda: custom_settings

    try:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["app_name"] == "Custom WORKLENS Test"
        assert data["environment"] == "testing"
        assert data["mock_mode"] is False
    finally:
        app.dependency_overrides.clear()

