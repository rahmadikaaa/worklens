"""Automated tests for WORKLENS Source Snapshot Versioning & History (P3)."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from app.config import Settings, get_settings
from app.main import app

client = TestClient(app)


@pytest.fixture
def snapshot_env(tmp_path: Path):
    """Provide isolated environment with temporary upload directory."""
    test_upload_dir = tmp_path / "uploads"
    test_upload_dir.mkdir(parents=True, exist_ok=True)
    settings = Settings(
        upload_dir=test_upload_dir,
        max_upload_size_bytes=5 * 1024 * 1024,
    )
    app.dependency_overrides[get_settings] = lambda: settings
    yield test_upload_dir
    app.dependency_overrides.clear()


def test_upload_creates_source_snapshot_json(snapshot_env: Path):
    """Verify that uploading a JSON file registers a new snapshot with complete metadata."""
    content = b'{"value": [{"activity_id": "ACT-1", "workload": 100}]}'
    filename = "assessment_batch.json"

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
    assert "snapshot_id" in data
    assert data["snapshot_id"].startswith("snap_")
    assert "source_id" in data

    # Verify snapshot metadata record on disk
    meta_file = snapshot_env / ".snapshots" / f"{data['snapshot_id']}.json"
    assert meta_file.exists()

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    assert meta["snapshot_id"] == data["snapshot_id"]
    assert meta["original_filename"] == filename
    assert meta["stored_filename"] == filename
    assert meta["file_format"] == "json"
    assert meta["file_size"] == len(content)
    assert meta["content_hash"] == hashlib.sha256(content).hexdigest()
    assert meta["status"] == "READY"
    assert meta["generated_at"] is None

    # Verify physical file is byte-for-byte identical
    stored_file = snapshot_env / data["saved_filename"]
    assert stored_file.read_bytes() == content


def test_upload_creates_source_snapshot_csv(snapshot_env: Path):
    """Verify that uploading a CSV file registers a snapshot with format 'csv'."""
    content = b"activity_id,app,workload\nACT-01,SAP,120\n"
    filename = "workload_sample.csv"

    response = client.post(
        "/api/v1/upload",
        files={"file": (filename, content, "text/csv")},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["file_format"] == "csv"
    assert data["snapshot"]["file_format"] == "csv"
    assert data["snapshot"]["content_hash"] == hashlib.sha256(content).hexdigest()


def test_breakdown_activity_pattern_extracts_generated_at(snapshot_env: Path):
    """Verify that 'breakdown_activity_MMDD_HHMM.json' extracts valid ISO generated_at."""
    content = b'{"value": []}'
    filename = "breakdown_activity_1105_1630.json"

    response = client.post(
        "/api/v1/upload",
        files={"file": (filename, content, "application/json")},
    )

    assert response.status_code == 201
    data = response.json()
    snapshot = data["snapshot"]

    assert snapshot["source_id"] == "breakdown_activity"
    assert snapshot["generated_at"] is not None

    current_year = datetime.now(timezone.utc).year
    expected_iso_prefix = f"{current_year}-11-05T16:30:00"
    assert snapshot["generated_at"].startswith(expected_iso_prefix)


def test_non_matching_filename_sets_generated_at_none(snapshot_env: Path):
    """Verify that non-matching filenames still succeed with generated_at = null."""
    test_filenames = [
        "custom_assessment.json",
        "breakdown_activity_invalid.json",
        "breakdown_activity_1105.json",
        "breakdown_activity.csv",
    ]

    for fname in test_filenames:
        mime = "application/json" if fname.endswith(".json") else "text/csv"
        response = client.post(
            "/api/v1/upload",
            files={"file": (fname, b'{"value": []}' if fname.endswith(".json") else b"a,b\n1,2\n", mime)},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["snapshot"]["generated_at"] is None


def test_invalid_date_in_pattern_sets_generated_at_none(snapshot_env: Path):
    """Verify that pattern with invalid calendar dates (e.g., month 13 or Feb 30) yields None."""
    content = b'{"value": []}'
    invalid_filenames = [
        "breakdown_activity_1301_1000.json",  # Month 13
        "breakdown_activity_0230_1000.json",  # Feb 30
        "breakdown_activity_1105_2500.json",  # Hour 25
    ]

    for fname in invalid_filenames:
        response = client.post(
            "/api/v1/upload",
            files={"file": (fname, content, "application/json")},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["snapshot"]["generated_at"] is None


def test_snapshot_immutability_and_no_overwriting(snapshot_env: Path):
    """Verify that uploading the same filename multiple times creates separate immutable snapshots."""
    content_v1 = b'{"value": [{"version": 1}]}'
    content_v2 = b'{"value": [{"version": 2}]}'
    filename = "activity_stream.json"

    # Upload 1
    res1 = client.post(
        "/api/v1/upload",
        files={"file": (filename, content_v1, "application/json")},
    )
    assert res1.status_code == 201
    snap1 = res1.json()

    # Upload 2 with same original filename
    res2 = client.post(
        "/api/v1/upload",
        files={"file": (filename, content_v2, "application/json")},
    )
    assert res2.status_code == 201
    snap2 = res2.json()

    # Snapshots must have distinct identifiers
    assert snap1["snapshot_id"] != snap2["snapshot_id"]
    assert snap1["saved_filename"] != snap2["saved_filename"]

    # Both files must exist on disk and retain exact contents
    file1_path = snapshot_env / snap1["saved_filename"]
    file2_path = snapshot_env / snap2["saved_filename"]
    assert file1_path.read_bytes() == content_v1
    assert file2_path.read_bytes() == content_v2

    # Both metadata records must exist independently
    meta1 = json.loads((snapshot_env / ".snapshots" / f"{snap1['snapshot_id']}.json").read_text(encoding="utf-8"))
    meta2 = json.loads((snapshot_env / ".snapshots" / f"{snap2['snapshot_id']}.json").read_text(encoding="utf-8"))
    assert meta1["content_hash"] == hashlib.sha256(content_v1).hexdigest()
    assert meta2["content_hash"] == hashlib.sha256(content_v2).hexdigest()


def test_list_snapshots_endpoint(snapshot_env: Path):
    """Verify listing snapshots ordered newest first and filtering by source_id."""
    # Upload 2 files
    client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1101_1000.json", b'{"value": []}', "application/json")},
    )
    client.post(
        "/api/v1/upload",
        files={"file": ("custom_source.csv", b"col1,col2\n1,2\n", "text/csv")},
    )

    res = client.get("/api/v1/snapshots")
    assert res.status_code == 200
    snapshots = res.json()
    assert len(snapshots) == 2

    # Verify descending ordering by uploaded_at
    assert snapshots[0]["uploaded_at"] >= snapshots[1]["uploaded_at"]

    # Filter by source_id
    res_filtered = client.get("/api/v1/snapshots?source_id=breakdown_activity")
    assert res_filtered.status_code == 200
    filtered_items = res_filtered.json()
    assert len(filtered_items) == 1
    assert filtered_items[0]["source_id"] == "breakdown_activity"


def test_get_snapshot_by_id_and_not_found(snapshot_env: Path):
    """Verify getting single snapshot metadata and 404 handling."""
    res_upload = client.post(
        "/api/v1/upload",
        files={"file": ("dataset.json", b'{"value": []}', "application/json")},
    )
    snap_id = res_upload.json()["snapshot_id"]

    res_get = client.get(f"/api/v1/snapshots/{snap_id}")
    assert res_get.status_code == 200
    assert res_get.json()["snapshot_id"] == snap_id

    # Nonexistent snapshot
    res_404 = client.get("/api/v1/snapshots/snap_nonexistent_999999")
    assert res_404.status_code == 404
    assert "not found" in res_404.json()["detail"].lower()


def test_snapshot_content_and_download_endpoints(snapshot_env: Path):
    """Verify secure retrieval of snapshot content and download attachment."""
    content = b'{"value": [{"id": 1, "name": "Test"}]}'
    res_upload = client.post(
        "/api/v1/upload",
        files={"file": ("test_doc.json", content, "application/json")},
    )
    snap_id = res_upload.json()["snapshot_id"]

    # Content endpoint
    res_content = client.get(f"/api/v1/snapshots/{snap_id}/content")
    assert res_content.status_code == 200
    assert res_content.content == content
    assert "application/json" in res_content.headers["content-type"]
    assert "inline" in res_content.headers.get("content-disposition", "")

    # Download endpoint
    res_download = client.get(f"/api/v1/snapshots/{snap_id}/download")
    assert res_download.status_code == 200
    assert res_download.content == content
    assert "attachment" in res_download.headers.get("content-disposition", "")


def test_snapshot_security_path_traversal(snapshot_env: Path):
    """Verify rejection of malicious snapshot_id path traversal patterns."""
    malicious_ids = [
        "../something",
        "..%2F..%2Fetc%2Fpasswd",
        "snap_123/evil",
        "snap_123\\evil",
        "snap_123;rm",
    ]

    for bad_id in malicious_ids:
        res = client.get(f"/api/v1/snapshots/{bad_id}")
        assert res.status_code in {400, 404}


def test_parse_snapshot_endpoint(snapshot_env: Path):
    """Verify parsing data schema directly from a selected snapshot."""
    raw_json = {
        "source": "PowerAutomate",
        "value": [
            {"activity_id": "ACT-A", "workload": 50, "app": "Jira"},
            {"activity_id": "ACT-B", "workload": 80, "app": "Slack"},
        ],
    }
    content = json.dumps(raw_json).encode("utf-8")

    res_upload = client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1105_1200.json", content, "application/json")},
    )
    snap_id = res_upload.json()["snapshot_id"]

    res_parse = client.post(f"/api/v1/snapshots/{snap_id}/parse")
    assert res_parse.status_code == 200
    parse_data = res_parse.json()

    assert parse_data["total_rows"] == 2
    assert parse_data["total_columns"] == 3
    assert "activity_id" in parse_data["columns"]
    assert parse_data["metadata"]["source"] == "PowerAutomate"
    assert parse_data["parsing_status"] == "success"

    # Verify source file is untouched
    stored_path = snapshot_env / res_upload.json()["saved_filename"]
    assert stored_path.read_bytes() == content


def test_parse_query_with_snapshot_id(snapshot_env: Path):
    """Verify parsing via query parameter ?snapshot_id=... on /api/v1/parse."""
    content = b"activity_id,dept,workload\nA1,Finance,100\nA2,HR,60\n"
    res_upload = client.post(
        "/api/v1/upload",
        files={"file": ("team_data.csv", content, "text/csv")},
    )
    snap_id = res_upload.json()["snapshot_id"]

    # Call /api/v1/parse?snapshot_id=...
    res_parse = client.post(f"/api/v1/parse?snapshot_id={snap_id}")
    assert res_parse.status_code == 200
    data = res_parse.json()
    assert data["file_format"] == "csv"
    assert data["total_rows"] == 2
    assert data["columns"] == ["activity_id", "dept", "workload"]

    # Calling without filename or snapshot_id returns 400
    res_err = client.post("/api/v1/parse")
    assert res_err.status_code == 400

