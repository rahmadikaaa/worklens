"""Automated unit and integration tests for WORKLENS Change Detection & Incremental Processing (P4)."""

import json
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from app.config import Settings, get_settings
from app.main import app
from app.services.change_detection_service import CURRENT_LOGIC_VERSION

client = TestClient(app)


@pytest.fixture
def p4_env(tmp_path: Path):
    """Provide isolated environment with temporary upload and runs storage directory."""
    test_upload_dir = tmp_path / "uploads"
    test_storage_dir = tmp_path / "runs"
    test_upload_dir.mkdir(parents=True, exist_ok=True)
    test_storage_dir.mkdir(parents=True, exist_ok=True)

    settings = Settings(
        upload_dir=test_upload_dir,
        storage_dir=test_storage_dir,
        max_upload_size_bytes=5 * 1024 * 1024,
    )
    app.dependency_overrides[get_settings] = lambda: settings
    yield test_upload_dir, test_storage_dir
    app.dependency_overrides.clear()


def test_no_change_identical_sha256(p4_env):
    """Verify that identical SHA-256 bypasses row parsing and is marked NO_CHANGE."""
    upload_dir, storage_dir = p4_env
    content = b'{"value": [{"activity_id": "ACT-1", "Workload": 100, "Workload after": 50}]}'

    # Upload Snapshot 1
    res1 = client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1101_1000.json", content, "application/json")},
    )
    snap1_id = res1.json()["snapshot_id"]

    # Process Snapshot 1
    proc1 = client.post(f"/api/v1/snapshots/{snap1_id}/process")
    assert proc1.status_code == 200

    # Upload Snapshot 2 with exact same bytes
    res2 = client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1101_1100.json", content, "application/json")},
    )
    snap2_id = res2.json()["snapshot_id"]

    # Compare Snapshot 2
    comp_res = client.post(f"/api/v1/snapshots/{snap2_id}/compare")
    assert comp_res.status_code == 200
    report = comp_res.json()

    assert report["status"] == "NO_CHANGE"
    assert report["identical_content_hash"] is True
    assert report["baseline_snapshot_id"] == snap1_id
    assert report["reprocess_count"] == 0

    # Process Snapshot 2
    proc2 = client.post(f"/api/v1/snapshots/{snap2_id}/process")
    assert proc2.status_code == 200
    p2_data = proc2.json()
    assert p2_data["status"] == "NO_CHANGE"
    assert p2_data["reprocessed_records"] == 0


def test_no_change_different_bytes_same_content(p4_env):
    """Verify that different file bytes with identical content is detected as NO_CHANGE."""
    content1 = b'{"value": [{"activity_id": "ACT-1", "Workload": 100, "Workload after": 50}]}'
    content2 = b'{\n  "value": [\n    {"Workload after": 50, "Workload": 100, "activity_id": "ACT-1"}\n  ]\n}'

    # Upload 1
    res1 = client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1101_1000.json", content1, "application/json")},
    )
    snap1_id = res1.json()["snapshot_id"]
    client.post(f"/api/v1/snapshots/{snap1_id}/process")

    # Upload 2
    res2 = client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1101_1100.json", content2, "application/json")},
    )
    snap2_id = res2.json()["snapshot_id"]

    # Compare
    comp = client.post(f"/api/v1/snapshots/{snap2_id}/compare").json()
    assert comp["status"] == "NO_CHANGE"
    assert comp["identical_content_hash"] is False
    assert comp["summary_counts"]["unchanged"] == 1
    assert comp["summary_counts"]["modified"] == 0
    assert comp["reprocess_count"] == 0


def test_change_detection_classifications_and_incremental_processing(p4_env):
    """Verify detection of UNCHANGED, MODIFIED, ADDED, DELETED and incremental execution."""
    upload_dir, storage_dir = p4_env

    # Baseline: ACT-1 (100 -> 50), ACT-2 (200 -> 100), ACT-DEL (80 -> 40)
    baseline_payload = {
        "value": [
            {"activity_id": "ACT-1", "Workload": 100, "Workload after": 50},
            {"activity_id": "ACT-2", "Workload": 200, "Workload after": 100},
            {"activity_id": "ACT-DEL", "Workload": 80, "Workload after": 40},
        ]
    }
    res1 = client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1101_1000.json", json.dumps(baseline_payload).encode(), "application/json")},
    )
    snap1_id = res1.json()["snapshot_id"]
    proc1 = client.post(f"/api/v1/snapshots/{snap1_id}/process")
    assert proc1.status_code == 200

    # New snapshot:
    # ACT-1: UNCHANGED (100 -> 50)
    # ACT-2: MODIFIED (Workload after changed to 150)
    # ACT-ADD: ADDED (300 -> 150)
    # ACT-DEL: omitted -> DELETED
    new_payload = {
        "value": [
            {"activity_id": "ACT-1", "Workload": 100, "Workload after": 50},
            {"activity_id": "ACT-2", "Workload": 200, "Workload after": 150},
            {"activity_id": "ACT-ADD", "Workload": 300, "Workload after": 150},
        ]
    }
    res2 = client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1101_1100.json", json.dumps(new_payload).encode(), "application/json")},
    )
    snap2_id = res2.json()["snapshot_id"]

    # 1. Compare endpoint
    comp_res = client.post(f"/api/v1/snapshots/{snap2_id}/compare")
    assert comp_res.status_code == 200
    report = comp_res.json()

    assert report["status"] == "CHANGES_DETECTED"
    assert report["summary_counts"]["unchanged"] == 1
    assert report["summary_counts"]["modified"] == 1
    assert report["summary_counts"]["added"] == 1
    assert report["summary_counts"]["deleted"] == 1
    assert report["reprocess_count"] == 2  # MODIFIED + ADDED

    # Verify change details
    changes_by_id = {c["activity_id"]: c for c in report["changes"]}
    assert changes_by_id["ACT-1"]["classification"] == "UNCHANGED"
    assert changes_by_id["ACT-2"]["classification"] == "MODIFIED"
    assert "Workload after" in changes_by_id["ACT-2"]["modified_fields"]
    assert changes_by_id["ACT-ADD"]["classification"] == "ADDED"
    assert changes_by_id["ACT-DEL"]["classification"] == "DELETED"

    # 2. Process endpoint
    proc_res = client.post(f"/api/v1/snapshots/{snap2_id}/process")
    assert proc_res.status_code == 200
    proc_data = proc_res.json()

    assert proc_data["status"] == "CHANGES_DETECTED"
    assert proc_data["reprocessed_records"] == 2
    assert proc_data["reused_records"] == 1
    assert proc_data["total_active_records"] == 3  # ACT-1, ACT-2, ACT-ADD (ACT-DEL excluded)

    # 3. Verify disk artifacts in runs directory
    run_id = proc_data["run_id"]
    run_dir = storage_dir / run_id
    assert run_dir.exists()

    change_log = json.loads((run_dir / "change_log.json").read_text(encoding="utf-8"))
    assert change_log["summary_counts"]["deleted"] == 1

    active_dataset = json.loads((run_dir / "enriched_dataset.json").read_text(encoding="utf-8"))
    active_ids = {r["activity_id"] for r in active_dataset}
    assert "ACT-DEL" not in active_ids
    assert active_ids == {"ACT-1", "ACT-2", "ACT-ADD"}

    # ACT-2 workload saved should be 200 - 150 = 50
    act2_rec = next(r for r in active_dataset if r["activity_id"] == "ACT-2")
    assert act2_rec["Workload Saved Est. (Min/Month)"] == 50.0


def test_review_required_on_empty_and_duplicate_activity_id(p4_env):
    """Verify that empty and duplicate activity_ids are flagged as REVIEW_REQUIRED."""
    payload = {
        "value": [
            {"activity_id": "ACT-VALID", "Workload": 100, "Workload after": 50},
            {"activity_id": "", "Workload": 60, "Workload after": 30},  # Empty ID
            {"activity_id": "ACT-DUP", "Workload": 80, "Workload after": 40},
            {"activity_id": "ACT-DUP", "Workload": 90, "Workload after": 45},  # Duplicate ID
        ]
    }
    res = client.post(
        "/api/v1/upload",
        files={"file": ("dataset_anomalies.json", json.dumps(payload).encode(), "application/json")},
    )
    snap_id = res.json()["snapshot_id"]

    comp = client.post(f"/api/v1/snapshots/{snap_id}/compare").json()
    assert comp["summary_counts"]["review_required"] == 3  # 1 empty + 2 duplicates
    assert comp["summary_counts"]["added"] == 1  # only ACT-VALID

    # Check reason flags
    empty_item = next(c for c in comp["changes"] if c["reason"] == "EMPTY_ACTIVITY_ID")
    assert empty_item["classification"] == "REVIEW_REQUIRED"

    dup_items = [c for c in comp["changes"] if c["reason"] == "DUPLICATE_ACTIVITY_ID"]
    assert len(dup_items) == 2

    # Run processing: review_required must be flagged, not auto-calculated
    proc = client.post(f"/api/v1/snapshots/{snap_id}/process").json()
    assert proc["summary_counts"]["review_required"] == 3


def test_logic_version_compatibility_triggers_recalculation(p4_env):
    """Verify that an outdated logic version in baseline invalidates reuse and recalculates."""
    upload_dir, storage_dir = p4_env

    # 1. Upload baseline snapshot
    content = b'{"value": [{"activity_id": "ACT-1", "Workload": 100, "Workload after": 50}]}'
    res1 = client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1101_1000.json", content, "application/json")},
    )
    snap1_id = res1.json()["snapshot_id"]
    proc1 = client.post(f"/api/v1/snapshots/{snap1_id}/process").json()

    # Manually tamper baseline run metadata with incompatible logic_version
    run1_dir = storage_dir / proc1["run_id"]
    meta_path = run1_dir / "run_metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["logic_version"] = "0.8.0"  # Incompatible version
    meta_path.write_text(json.dumps(meta), encoding="utf-8")

    # 2. Upload snapshot 2 (same data content, but slightly different formatting)
    content2 = b'{"value": [{"activity_id": "ACT-1", "Workload": 100, "Workload after": 50}], "v": 2}'
    res2 = client.post(
        "/api/v1/upload",
        files={"file": ("breakdown_activity_1101_1100.json", content2, "application/json")},
    )
    snap2_id = res2.json()["snapshot_id"]

    # 3. Process snapshot 2: because version was 0.8.0, it must recalculate instead of reusing
    proc2 = client.post(f"/api/v1/snapshots/{snap2_id}/process").json()
    assert proc2["reprocessed_records"] == 1
    assert proc2["reused_records"] == 0


def test_runs_api_endpoints(p4_env):
    """Verify /api/v1/runs and /api/v1/runs/{run_id} endpoints."""
    content = b'{"value": [{"activity_id": "ACT-TEST", "Workload": 120, "Workload after": 60}]}'
    res_up = client.post(
        "/api/v1/upload",
        files={"file": ("batch_sample.json", content, "application/json")},
    )
    snap_id = res_up.json()["snapshot_id"]
    proc_res = client.post(f"/api/v1/snapshots/{snap_id}/process")
    run_id = proc_res.json()["run_id"]

    # List runs
    runs_res = client.get("/api/v1/runs")
    assert runs_res.status_code == 200
    runs = runs_res.json()
    assert any(r["run_id"] == run_id for r in runs)

    # Get single run detail
    single_res = client.get(f"/api/v1/runs/{run_id}")
    assert single_res.status_code == 200
    assert single_res.json()["run_id"] == run_id

    # Nonexistent run -> 404
    err_res = client.get("/api/v1/runs/run_nonexistent_9999")
    assert err_res.status_code == 404

