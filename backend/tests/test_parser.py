"""Automated tests for WORKLENS File Parser API (P2)."""

import json
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from app.config import Settings, get_settings
from app.main import app

client = TestClient(app)


@pytest.fixture
def parser_env(tmp_path: Path):
    """Provide isolated environment with sample files in a temporary upload directory."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    settings = Settings(
        upload_dir=upload_dir,
        max_upload_size_bytes=5 * 1024 * 1024,
    )
    app.dependency_overrides[get_settings] = lambda: settings
    yield upload_dir
    app.dependency_overrides.clear()


def test_parse_json_envelope_with_value(parser_env: Path):
    """Verify parsing JSON object with metadata and 'value' array (Structure A)."""
    raw_content = {
        "source_workbook": "assessment_2026.xlsx",
        "sheet_name": "Operations",
        "extracted_at": "2026-11-05T10:00:00Z",
        "total_rows": 2,
        "columns_detected": 4,
        "value": [
            {"activity_id": "ACT-001", "application": "Billing", "workload": 120, "workload_after": 60},
            {"activity_id": "ACT-002", "application": "CRM", "workload": 90, "workload_after": 30},
        ],
    }
    file_path = parser_env / "envelope.json"
    file_bytes = json.dumps(raw_content).encode("utf-8")
    file_path.write_bytes(file_bytes)

    res = client.post(f"/api/v1/parse/{file_path.name}")
    assert res.status_code == 200
    data = res.json()

    assert data["filename"] == "envelope.json"
    assert data["file_format"] == "json"
    assert data["total_rows"] == 2
    assert data["total_columns"] == 4
    assert data["columns"] == ["activity_id", "application", "workload", "workload_after"]
    assert data["metadata"]["source_workbook"] == "assessment_2026.xlsx"
    assert data["metadata"]["sheet_name"] == "Operations"
    assert data["metadata"]["extracted_at"] == "2026-11-05T10:00:00Z"
    assert data["parsing_status"] == "success"

    # Verify source file is untouched
    assert file_path.read_bytes() == file_bytes


def test_parse_json_top_level_array(parser_env: Path):
    """Verify parsing JSON top-level array of record objects (Structure B)."""
    raw_content = [
        {"activity_id": "ACT-101", "type": "Manual Data Entry", "hours": 4.5},
        {"activity_id": "ACT-102", "type": "Reconciliation", "hours": 2.0, "extra_note": "Daily"},
    ]
    file_path = parser_env / "array.json"
    file_bytes = json.dumps(raw_content).encode("utf-8")
    file_path.write_bytes(file_bytes)

    res = client.get(f"/api/v1/parse/{file_path.name}")
    assert res.status_code == 200
    data = res.json()

    assert data["filename"] == "array.json"
    assert data["file_format"] == "json"
    assert data["total_rows"] == 2
    assert data["total_columns"] == 4
    assert data["columns"] == ["activity_id", "type", "hours", "extra_note"]
    assert data["metadata"] == {}
    assert data["parsing_status"] == "success"
    assert file_path.read_bytes() == file_bytes


def test_parse_csv_comma_delimiter(parser_env: Path):
    """Verify parsing CSV file with comma delimiter."""
    csv_text = "activity_id,application,workload\nACT-01,SAP,150\nACT-02,Salesforce,80\n"
    file_path = parser_env / "comma.csv"
    file_path.write_bytes(csv_text.encode("utf-8"))

    res = client.post(f"/api/v1/parse/{file_path.name}")
    assert res.status_code == 200
    data = res.json()

    assert data["filename"] == "comma.csv"
    assert data["file_format"] == "csv"
    assert data["total_rows"] == 2
    assert data["total_columns"] == 3
    assert data["columns"] == ["activity_id", "application", "workload"]
    assert data["parsing_status"] == "success"


def test_parse_csv_semicolon_delimiter(parser_env: Path):
    """Verify parsing CSV file with semicolon delimiter."""
    csv_text = "activity_id;application;workload;workload_after\nACT-01;SAP;150;50\nACT-02;Legacy;200;100\n"
    file_path = parser_env / "semicolon.csv"
    file_path.write_bytes(csv_text.encode("utf-8"))

    res = client.post(f"/api/v1/parse/{file_path.name}")
    assert res.status_code == 200
    data = res.json()

    assert data["filename"] == "semicolon.csv"
    assert data["file_format"] == "csv"
    assert data["total_rows"] == 2
    assert data["total_columns"] == 4
    assert data["columns"] == ["activity_id", "application", "workload", "workload_after"]


def test_parse_utf8_bom(parser_env: Path):
    """Verify parsing file encoded in UTF-8 with BOM."""
    csv_text = "activity_id,name\nACT-BOM,BOM Test\n"
    file_path = parser_env / "bom.csv"
    file_path.write_bytes(csv_text.encode("utf-8-sig"))

    res = client.post(f"/api/v1/parse/{file_path.name}")
    assert res.status_code == 200
    data = res.json()

    assert data["total_rows"] == 1
    assert data["columns"] == ["activity_id", "name"]
    # Ensure BOM character is not part of the first column name
    assert not data["columns"][0].startswith("\ufeff")


def test_parse_windows_1252(parser_env: Path):
    """Verify parsing CSV file encoded in Windows-1252."""
    # Contains Windows-1252 character (café with \xe9)
    csv_bytes = "activity_id,description\nACT-CP,V\xe9rification des donn\xe9es\n".encode("cp1252")
    file_path = parser_env / "cp1252.csv"
    file_path.write_bytes(csv_bytes)

    res = client.post(f"/api/v1/parse/{file_path.name}")
    assert res.status_code == 200
    data = res.json()

    assert data["total_rows"] == 1
    assert data["columns"] == ["activity_id", "description"]


def test_parse_invalid_json(parser_env: Path):
    """Verify error handling on invalid JSON syntax."""
    file_path = parser_env / "broken.json"
    file_path.write_bytes(b'{"key": "unclosed')

    res = client.post(f"/api/v1/parse/{file_path.name}")
    assert res.status_code == 400
    assert "Invalid JSON syntax" in res.json()["detail"]


def test_parse_empty_file(parser_env: Path):
    """Verify error handling on 0-byte file."""
    file_path = parser_env / "empty.json"
    file_path.write_bytes(b"")

    res = client.post(f"/api/v1/parse/{file_path.name}")
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


def test_parse_unsupported_json_structure(parser_env: Path):
    """Verify rejection of unsupported JSON structures (e.g. primitive array, arbitrary dict)."""
    # 1. Arbitrary dict without 'value'
    f1 = parser_env / "no_value.json"
    f1.write_bytes(b'{"some_key": 123}')
    res1 = client.post(f"/api/v1/parse/{f1.name}")
    assert res1.status_code == 400
    assert "Unsupported JSON structure" in res1.json()["detail"]

    # 2. Primitive array
    f2 = parser_env / "primitives.json"
    f2.write_bytes(b'[1, 2, 3]')
    res2 = client.post(f"/api/v1/parse/{f2.name}")
    assert res2.status_code == 400
    assert "Unsupported JSON structure" in res2.json()["detail"]


def test_parse_malformed_csv(parser_env: Path):
    """Verify error handling on malformed CSV (e.g. unclosed quote or NUL byte)."""
    f = parser_env / "malformed.csv"
    # Unclosed quote
    f.write_bytes(b'col1,col2\n"unclosed quote,val2\n')
    res = client.post(f"/api/v1/parse/{f.name}")
    assert res.status_code == 400
    assert "Malformed CSV" in res.json()["detail"]


def test_parse_file_not_found(parser_env: Path):
    """Verify HTTP 404 when file does not exist in upload directory."""
    res = client.post("/api/v1/parse/non_existent.json")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_parse_path_traversal(parser_env: Path):
    """Verify rejection of path traversal attempts."""
    traversals = [
        "../test.json",
        "..\\test.json",
        "../../etc/passwd.json",
    ]
    for filename in traversals:
        # Test via query parameter endpoint to ensure path is passed without client-side URI normalization
        res = client.post("/api/v1/parse", params={"filename": filename})
        assert res.status_code == 400
        assert "path traversal" in res.json()["detail"].lower()

    # Test via path parameter with URL-encoded traversal
    res_path = client.post("/api/v1/parse/..%2Ftest.json")
    assert res_path.status_code == 400
    assert "path traversal" in res_path.json()["detail"].lower()
