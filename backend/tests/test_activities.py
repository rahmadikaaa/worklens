"""Tests for Activities and Workload exploration endpoints (V1)."""

from fastapi.testclient import TestClient
from app.main import create_application

app = create_application()
client = TestClient(app)


def test_get_activities_summary():
    """Verify activities summary returns valid schema and metrics."""
    res = client.get("/api/v1/activities/summary")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "filter_options" in data
    summary = data["summary"]
    assert summary["total_activities"] > 0
    assert "distribution_criticality" in summary
    assert "distribution_automation" in summary


def test_query_activities_pagination_and_search():
    """Verify querying activities supports search, pagination, and sorting."""
    res = client.get("/api/v1/activities?page=1&page_size=10&sort_by=APPS&sort_order=asc")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) <= 10
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_count"] > 0


def test_get_single_activity_detail():
    """Verify single activity lookup by activity_id."""
    res_list = client.get("/api/v1/activities?page=1&page_size=1")
    assert res_list.status_code == 200
    items = res_list.json()["items"]
    assert len(items) > 0
    first_id = items[0]["activity_id"]

    res_single = client.get(f"/api/v1/activities/{first_id}")
    assert res_single.status_code == 200
    single = res_single.json()
    assert single["activity_id"] == first_id
    assert "Workload Calculation Status" in single


def test_automation_opportunity_metrics_and_buckets():
    """Verify opportunity KPIs, bucket distributions, and Pareto curve from reference."""
    res = client.get("/api/v1/activities/summary")
    assert res.status_code == 200
    summary = res.json()["summary"]

    assert "opportunity_kpis" in summary
    kpis = summary["opportunity_kpis"]
    assert kpis["total_workload_hours"] == 3602.0
    assert kpis["measured_activities_count"] == 1475
    assert kpis["candidate_workload_hours"] == 357.5
    assert kpis["candidate_activities_count"] == 200
    assert abs(kpis["indicative_saving_hours"] - 321.75) <= 0.1

    assert "buckets" in summary
    bucket_map = {b["k"]: b for b in summary["buckets"]}
    assert "Kandidat" in bucket_map
    assert bucket_map["Kandidat"]["h"] == 357.5
    assert bucket_map["Sudah diotomasi"]["h"] == 1993.7
    assert bucket_map["Tidak mungkin diotomasi"]["h"] == 811.9
    assert bucket_map["Take Out"]["h"] == 267.6
    assert bucket_map["Dismantled"]["h"] == 171.3

    assert "pareto" in summary
    assert len(summary["pareto"]) > 0
    top1 = summary["pareto"][0]
    assert top1["n"] == 1
    assert top1["p"] == 12.7

    # Test filtering by bucket
    res_filtered = client.get("/api/v1/activities?bucket=Kandidat&has_workload=true&page_size=10")
    assert res_filtered.status_code == 200
    filtered_data = res_filtered.json()
    assert filtered_data["total_count"] == 200
    assert all(item["automation_bucket"] == "Kandidat" for item in filtered_data["items"])


def test_dashboard_enhancement_meeting_oktober_scopes():
    """Verify all 7 enhancement scopes: Reality Check, Quick-Wins, Baseline, Outliers, Tech, Trigger, Benefit."""
    res = client.get("/api/v1/activities/summary")
    assert res.status_code == 200
    summary = res.json()["summary"]

    # 1. Reality Check
    assert "reality_check" in summary
    rc = summary["reality_check"]
    assert rc["theoretical_claimed_hours"] == 3156.3
    assert rc["theoretical_claimed_pct"] == 87.6
    assert rc["real_actionable_hours"] == 357.5
    assert abs(rc["real_savings_estimate_hours"] - 321.75) <= 0.1
    assert rc["out_of_scope_workload_pct"] == 90.1

    # 2. Quick-Wins
    assert "quick_wins_summary" in summary
    qw = summary["quick_wins_summary"]
    assert qw["total_count"] > 0
    assert qw["to_be_automated_hours"] == 92.8

    # 3. Trigger Readiness
    assert "trigger_readiness_summary" in summary
    tr = summary["trigger_readiness_summary"]
    assert tr["fully_automated_count"] == 389
    assert tr["not_yet_triggered_count"] == 256
    assert tr["partial_automated_count"] == 22
    assert tr["baseline_total"] == 667

    # 4. Outlier Detection
    assert "outliers_summary" in summary
    assert len(summary["outliers_summary"]) >= 1
    top_outlier = summary["outliers_summary"][0]
    assert "Office 365" in top_outlier["app"]
    assert top_outlier["workload_hours"] == 456.0

    # 5. Technology & Candidate Apps
    assert "candidate_technologies" in summary
    assert len(summary["candidate_technologies"]) > 0
    assert "top_candidate_apps" in summary
    assert any(app["app"] == "UFO" for app in summary["top_candidate_apps"])

    # 6. Query filtering with new params
    # Test quick-win filter
    res_qw = client.get("/api/v1/activities?quick_win_only=true")
    assert res_qw.status_code == 200
    qw_items = res_qw.json()["items"]
    assert all(item["is_quick_win"] is True for item in qw_items)

    # Test outlier filter
    res_out = client.get("/api/v1/activities?outlier_only=true")
    assert res_out.status_code == 200
    out_items = res_out.json()["items"]
    assert len(out_items) >= 1
    assert out_items[0]["is_outlier"] is True

    # Test verified baseline filter
    res_base = client.get("/api/v1/activities?verified_baseline_only=true&page_size=5")
    assert res_base.status_code == 200
    base_items = res_base.json()["items"]
    assert all(item["is_verified_baseline"] is True for item in base_items)
    assert all(item["benefit_statement"] is not None for item in base_items)



