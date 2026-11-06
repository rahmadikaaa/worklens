"""Automated tests for WORKLENS File Upload API (P1)."""

from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from app.config import Settings, get_settings
from app.main import app

client = TestClient(app)


@pytest.fixture
def temp_upload_settings(tmp_path: Path):
    """Provide isolated settings with a temporary upload directory."""
    test_upload_dir = tmp_path / "uploads"
    settings = Settings(
        upload_dir=test_upload_dir,
        max_upload_size_bytes=1024 * 1024,  # 1 MB for testing
    )
    app.dependency_overrides[get_settings] = lambda: settings
    yield settings
    app.dependency_overrides.clear()


def test_upload_json_success(temp_upload_settings: Settings):
    """Verify successful upload of a JSON assessment file."""
    content = b'{"activities": [{"activity_id": "ACT-001", "workload": 120}]}'
    filename = "assessment_data.json"

    response = client.post(
        "/api/v1/upload",
        files={"file": (filename, content, "application/json")},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == filename
    assert data["saved_filename"] == filename
    assert data["file_format"] == "json"
    assert data["file_size"] == len(content)
    assert data["upload_status"] == "success"
    assert "uploaded_at" in data

    # Verify physical file on disk matches original bytes exactly
    saved_file = temp_upload_settings.upload_dir / data["saved_filename"]
    assert saved_file.exists()
    assert saved_file.read_bytes() == content


def test_upload_csv_success(temp_upload_settings: Settings):
    """Verify successful upload of a CSV assessment file."""
    content = b"activity_id,workload,workload_after\nACT-001,100,50\n"
    filename = "assessment_data.csv"

    response = client.post(
        "/api/v1/upload",
        files={"file": (filename, content, "text/csv")},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == filename
    assert data["saved_filename"] == filename
    assert data["file_format"] == "csv"
    assert data["file_size"] == len(content)
    assert data["upload_status"] == "success"

    # Verify physical file on disk matches original bytes exactly
    saved_file = temp_upload_settings.upload_dir / data["saved_filename"]
    assert saved_file.exists()
    assert saved_file.read_bytes() == content


def test_upload_unsupported_file_extension(temp_upload_settings: Settings):
    """Verify rejection when file extension is not .json or .csv."""
    unsupported_files = [
        ("report.txt", b"plain text", "text/plain"),
        ("program.exe", b"binary content", "application/octet-stream"),
        ("document.pdf", b"%PDF-1.4", "application/pdf"),
        ("sheet.xlsx", b"excel binary", "application/vnd.ms-excel"),
    ]

    for name, content, mime in unsupported_files:
        response = client.post(
            "/api/v1/upload",
            files={"file": (name, content, mime)},
        )
        assert response.status_code == 400
        assert "Unsupported file extension" in response.json()["detail"]


def test_upload_empty_file(temp_upload_settings: Settings):
    """Verify rejection when uploaded file has 0 bytes."""
    response = client.post(
        "/api/v1/upload",
        files={"file": ("empty.json", b"", "application/json")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_oversized_file(temp_upload_settings: Settings):
    """Verify rejection with HTTP 413 when file exceeds max permitted size."""
    # Settings fixture sets max_upload_size_bytes to 1 MB (1048576 bytes)
    oversized_content = b"x" * (1024 * 1024 + 10)  # Exceeds 1 MB

    response = client.post(
        "/api/v1/upload",
        files={"file": ("large_assessment.json", oversized_content, "application/json")},
    )
    assert response.status_code == 413
    assert "exceeds maximum allowed limit" in response.json()["detail"].lower()


def test_upload_invalid_content_type(temp_upload_settings: Settings):
    """Verify rejection when MIME content type does not match file extension."""
    # JSON file with image MIME
    response = client.post(
        "/api/v1/upload",
        files={"file": ("data.json", b'{"test": 1}', "image/png")},
    )
    assert response.status_code == 400
    assert "Invalid content type" in response.json()["detail"]

    # CSV file with JSON MIME
    response = client.post(
        "/api/v1/upload",
        files={"file": ("data.csv", b"id,val\n1,2", "application/json")},
    )
    assert response.status_code == 400
    assert "Invalid content type" in response.json()["detail"]


def test_upload_duplicate_filename_handling(temp_upload_settings: Settings):
    """Verify collision safety: duplicate uploads are preserved with unique filenames."""
    content_first = b'{"version": 1}'
    content_second = b'{"version": 2}'
    filename = "dataset.json"

    # First upload
    res1 = client.post(
        "/api/v1/upload",
        files={"file": (filename, content_first, "application/json")},
    )
    assert res1.status_code == 201
    saved_name_1 = res1.json()["saved_filename"]
    assert saved_name_1 == "dataset.json"

    # Second upload with same original filename
    res2 = client.post(
        "/api/v1/upload",
        files={"file": (filename, content_second, "application/json")},
    )
    assert res2.status_code == 201
    saved_name_2 = res2.json()["saved_filename"]
    assert saved_name_2 == "dataset_1.json"
    assert saved_name_1 != saved_name_2

    # Third upload with same original filename
    res3 = client.post(
        "/api/v1/upload",
        files={"file": (filename, b'{"version": 3}', "application/json")},
    )
    assert res3.status_code == 201
    saved_name_3 = res3.json()["saved_filename"]
    assert saved_name_3 == "dataset_2.json"

    # Verify all physical files exist and contents are intact
    dir_path = temp_upload_settings.upload_dir
    assert (dir_path / saved_name_1).read_bytes() == content_first
    assert (dir_path / saved_name_2).read_bytes() == content_second
    assert (dir_path / saved_name_3).read_bytes() == b'{"version": 3}'


def test_upload_path_traversal_sanitization(temp_upload_settings: Settings):
    """Verify malicious filenames with path traversal characters are sanitized."""
    content = b'{"safe": true}'
    malicious_filename = "../../../etc/passwd.json"

    response = client.post(
        "/api/v1/upload",
        files={"file": (malicious_filename, content, "application/json")},
    )
    assert response.status_code == 201
    data = response.json()
    assert "/" not in data["saved_filename"]
    assert "\\" not in data["saved_filename"]
    assert not data["saved_filename"].startswith("..")

    # Stored file must reside safely inside temp_upload_dir
    saved_file = temp_upload_settings.upload_dir / data["saved_filename"]
    assert saved_file.exists()
    assert saved_file.read_bytes() == content


def test_upload_failure_handling(temp_upload_settings: Settings):
    """Verify HTTP 500 when file cannot be written to disk."""
    content = b'{"test": "failure"}'

    with patch("builtins.open", side_effect=OSError("Disk write error")):
        response = client.post(
            "/api/v1/upload",
            files={"file": ("error_test.json", content, "application/json")},
        )
        assert response.status_code == 500
        assert "Failed to save uploaded file to disk" in response.json()["detail"]


def test_upload_alias_endpoint(temp_upload_settings: Settings):
    """Verify /api/v1/uploads alias functions identically to /api/v1/upload."""
    content = b'{"alias": true}'
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("alias_test.json", content, "application/json")},
    )
    assert response.status_code == 201
    assert response.json()["filename"] == "alias_test.json"

