"""Tests for Reverse Engineering Enrichment Discovery endpoint."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_enrichment_discovery_success():
    """Verify that enrichment discovery returns 100% matched validation results."""
    response = client.get("/api/v1/enrichment/discovery")
    assert response.status_code == 200
    data = response.json()

    # Executive Summary checks
    exec_summary = data["executive_summary"]
    assert exec_summary["status"] == "VALIDATED_100_PERCENT"
    assert exec_summary["total_benchmark_records"] == 667
    assert exec_summary["match_rate_percent"] == 100.0
    assert exec_summary["workload_formula_accuracy_percent"] == 100.0
    assert exec_summary["benefit_text_accuracy_percent"] == 100.0

    # Matching checks
    matching = data["matching_results"]
    assert matching["exact_matches"] == 658
    assert matching["stripped_matches"] == 9
    assert matching["unmatched_count"] == 0

    # Rule Catalog checks
    rule_catalog = data["rule_catalog"]
    assert len(rule_catalog) >= 12
    rule_ids = [r["id"] for r in rule_catalog]
    assert "RULE-WL-01" in rule_ids
    assert "RULE-BEN-01" in rule_ids
    assert "RULE-INF-01" in rule_ids

    # Confidence summary checks
    conf = data["confidence_summary"]
    assert "CONFIRMED" in conf
    assert "INFERRED" in conf
    assert "UNRESOLVED" in conf
    assert conf["CONFIRMED"]["count"] >= 8

    # Decision table checks
    decision_table = data["decision_table"]
    assert len(decision_table) >= 8

    # Exception checks (2 numeric overrides + 9 whitespace cases = 11)
    exceptions = data["exception_analysis"]
    assert len(exceptions) == 11

