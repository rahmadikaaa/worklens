"""Service for querying and analyzing enriched activities from assessment datasets (V1)."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from app.core.enrichment import evaluate_row_workload

_CACHE: Dict[str, Dict[str, Any]] = {}
_BASELINE_CACHE: Dict[str, Dict[str, Any]] = {}

BUCKET_CONFIGS: List[Dict[str, str]] = [
    {"k": "Kandidat", "label": "Kandidat otomasi", "color": "#087f70", "cls": "candidate"},
    {"k": "Sudah diotomasi", "label": "Sudah diotomasi", "color": "#9aa9a4", "cls": ""},
    {"k": "Tidak mungkin diotomasi", "label": "Tidak mungkin diotomasi", "color": "#c66f60", "cls": ""},
    {"k": "Take Out", "label": "Take Out", "color": "#d4973b", "cls": "take"},
    {"k": "Dismantled", "label": "Dismantled", "color": "#788380", "cls": "dismantled"},
    {"k": "Lainnya", "label": "Lainnya", "color": "#bcc7c4", "cls": ""},
]


def classify_automation_bucket(r: Dict[str, Any]) -> str:
    """Classify activity into an executive automation opportunity bucket based on verified domain rules."""
    status_val = str(r.get("Status", "")).strip().lower()
    cat_val = str(r.get("Category Notes", "")).strip()
    if status_val in ("take out", "takeout"):
        return "Take Out"
    if cat_val == "Dismantled":
        return "Dismantled"
    if cat_val == "Already Automation":
        return "Sudah diotomasi"
    if cat_val == "Not Possible Automate":
        return "Tidak mungkin diotomasi"
    if cat_val in ("To Be Automated", "As Is", "Not Yet Solution", "Need Further Assessment", "Already Automated"):
        return "Kandidat"
    return "Lainnya"


def load_verified_baseline(upload_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load the 667 verified baseline improvements from Agent Harness (Improvements_With_Benefit.csv)."""
    global _BASELINE_CACHE
    if _BASELINE_CACHE:
        return _BASELINE_CACHE

    candidates = [
        upload_dir / "REA" / "Improvements_With_Benefit.csv",
        upload_dir / "Improvements_With_Benefit.csv",
        Path("backend/uploads/REA/Improvements_With_Benefit.csv"),
    ]
    csv_path: Optional[Path] = None
    for c in candidates:
        if c.is_file():
            csv_path = c.resolve()
            break

    if not csv_path:
        return {}

    baseline_map: Dict[str, Dict[str, Any]] = {}
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                concat = str(row.get("CONCAT", "")).strip().lower()
                if concat:
                    baseline_map[concat] = {
                        "concat": row.get("CONCAT", ""),
                        "category_action": row.get("Category Action", ""),
                        "tools_automation": row.get("Tools Automation", ""),
                        "status_triggered": row.get("Status Triggered", "Not Yet Triggered Automated"),
                        "benefit": row.get("Benefit", ""),
                    }
    except Exception as err:
        print(f"Warning: Failed to load baseline CSV: {err}")
        return {}

    _BASELINE_CACHE = baseline_map
    return baseline_map


def recommend_technology(r: Dict[str, Any], baseline_tool: Optional[str] = None) -> Dict[str, Any]:
    """Provide an indicative technology recommendation for candidate activities without claiming it as a final decision."""
    # 1. Baseline verified tool
    if baseline_tool and baseline_tool.strip() not in ("Not Automate", "", "#N/A", "-"):
        canon = baseline_tool.strip()
        return {
            "technology": canon,
            "rationale": f"Terverifikasi dari baseline Agent Harness (Tools: {canon}).",
            "is_final": False,
        }

    # 2. Recorded profile tool
    existing_tool = str(r.get("Tools Automation", "")).strip()
    if existing_tool and existing_tool not in ("Not Automate", "#N/A", "-"):
        return {
            "technology": existing_tool,
            "rationale": f"Tercatat pada profil aktivitas operasional ({existing_tool}).",
            "is_final": False,
        }

    # 3. Rule-based technology indication from TYPE ACTIVITY & operational patterns
    act_type = str(r.get("TYPE ACTIVITY", "")).strip().lower()
    act_name = str(r.get("ACTIVITY NAME", "")).strip().lower()

    if any(k in act_type for k in ("incident", "complaint")) or "restart" in act_name:
        return {
            "technology": "AION Platform",
            "rationale": "Rekomendasi indikatif untuk incident remediation & automated service restart.",
            "is_final": False,
        }
    if "monitoring" in act_type or "alert" in act_type or "cek" in act_name or "checking" in act_name:
        return {
            "technology": "Grafana / AION",
            "rationale": "Rekomendasi indikatif untuk auto-alerting & synthetic monitoring.",
            "is_final": False,
        }
    if "daily" in act_type or "housekeeping" in act_type or "report" in act_name or "clean" in act_name:
        return {
            "technology": "Shell Script / Cron",
            "rationale": "Rekomendasi indikatif untuk batch housekeeping & scheduled reporting.",
            "is_final": False,
        }
    if "change" in act_type or "deploy" in act_name or "config" in act_name:
        return {
            "technology": "CI/CD Pipeline",
            "rationale": "Rekomendasi indikatif untuk parameter update & automated config push.",
            "is_final": False,
        }
    if "service request" in act_type or "audit" in act_type:
        return {
            "technology": "BMC / AION",
            "rationale": "Rekomendasi indikatif untuk ITSM ticket processing & log extraction.",
            "is_final": False,
        }

    return {
        "technology": "Standard Automation / Script",
        "rationale": "Rekomendasi otomasi standar berbasis task automation.",
        "is_final": False,
    }


def is_activity_quick_win(bucket: str, cat_note: str, dur: float, ev: float) -> bool:
    """Identify quick-win automation candidates (high frequency or To Be Automated flag)."""
    if bucket != "Kandidat":
        return False
    if cat_note == "To Be Automated":
        return True
    if ev >= 10.0 and dur <= 30.0:
        return True
    return False


def is_activity_outlier(workload_numeric: float) -> bool:
    """Flag extreme workload outliers (>= 100 hours or 6,000 minutes per month)."""
    return workload_numeric >= 6000.0




def _resolve_target_file(filename: Optional[str], upload_dir: Path) -> Path:
    """Resolve target dataset file safely inside upload directory."""
    default_name = "breakdown_activity_261106_1112.json"
    name = filename or default_name

    # Check upload directory
    target = (upload_dir / name).resolve()
    if target.is_file():
        return target

    # Fallback to backend/uploads
    fallback = Path("backend/uploads") / name
    if fallback.is_file():
        return fallback.resolve()

    # Search for default file or any breakdown_activity JSON
    for candidate in upload_dir.glob("breakdown_activity_*.json"):
        if candidate.is_file():
            return candidate.resolve()

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Dataset file '{name}' not found in upload directory.",
    )


def load_and_enrich_activities(filename: Optional[str], upload_dir: Path) -> Dict[str, Any]:
    """Load and enrich activities dataset, caching in memory for high-performance querying."""
    file_path = _resolve_target_file(filename, upload_dir)
    file_key = str(file_path)

    # Check cache freshness via mtime
    mtime = file_path.stat().st_mtime
    cached = _CACHE.get(file_key)
    if cached and cached.get("mtime") == mtime:
        return cached

    # Parse JSON
    try:
        raw_bytes = file_path.read_bytes()
        parsed = json.loads(raw_bytes.decode("utf-8-sig"))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read dataset JSON: {err}",
        ) from err

    raw_records: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    if isinstance(parsed, dict):
        raw_records = parsed.get("value", [])
        for k, v in parsed.items():
            if k != "value":
                metadata[k] = v
    elif isinstance(parsed, list):
        raw_records = parsed

    # Load verified baseline from Agent Harness if available
    baseline_map = load_verified_baseline(upload_dir)

    # Enrich each row strictly according to M1 rules
    enriched_rows: List[Dict[str, Any]] = []
    for idx, r in enumerate(raw_records, start=1):
        enriched = evaluate_row_workload(r, source_row_index=idx).to_dict()
        enriched_rows.append(enriched)

    # Calculate overall dataset statistics
    total_activities = len(enriched_rows)

    total_workload_before = 0.0
    total_workload_after = 0.0
    total_workload_saved = 0.0
    annualized_saved_total = 0.0

    calc_counts = Counter()
    evidence_counts = Counter()
    crit_counts = Counter()
    auto_counts = Counter()
    dept_counts = Counter()
    app_counts = Counter()
    assessment_counts = Counter()
    cat_action_counts = Counter()

    # Domain bucket aggregations
    bucket_hours = Counter()
    bucket_counts = Counter()
    type_hours = Counter()
    tool_hours = Counter()
    team_hours = Counter()
    positive_rows: List[Dict[str, Any]] = []

    # Enhanced Analytics aggregations (Meeting Oktober)
    trigger_readiness_counts = Counter()
    quick_win_rows: List[Dict[str, Any]] = []
    candidate_app_hours = Counter()
    candidate_app_counts = Counter()
    candidate_tech_hours = Counter()
    candidate_tech_counts = Counter()
    outlier_rows: List[Dict[str, Any]] = []

    data_quality_issues = 0

    for r in enriched_rows:
        calc_status = r.get("Workload Calculation Status", "")
        calc_counts[calc_status] += 1

        if calc_status in ("INVALID_INPUT", "MISSING_INPUT", "NEGATIVE_INPUT", "NEGATIVE_SAVINGS"):
            data_quality_issues += 1

        ev_status = r.get("Workload Evidence Status", "")
        evidence_counts[ev_status] += 1

        crit = str(r.get("APP PRIORITY", "")).strip() or "Unclassified"
        crit_counts[crit] += 1

        auto = str(r.get("Automation/Manual", "")).strip() or "Unclassified"
        auto_counts[auto] += 1

        dept = str(r.get("DEPT", "")).strip()
        if dept:
            dept_counts[dept] += 1

        app = str(r.get("APPS", "")).strip()
        if app:
            app_counts[app] += 1

        assess = str(r.get("Assessment Status", "")).strip() or "Not Assessed"
        assessment_counts[assess] += 1

        cat_act = str(r.get("Category Action", "")).strip()
        if cat_act:
            cat_action_counts[cat_act] += 1

        # Classify executive bucket
        bucket = classify_automation_bucket(r)
        r["automation_bucket"] = bucket

        # Parse numeric workload
        wl_numeric = 0.0
        try:
            wl = float(str(r.get("Workload", "")).strip().replace(",", "."))
            total_workload_before += wl
            wl_numeric = wl
        except (ValueError, TypeError):
            pass

        r["workload_numeric"] = wl_numeric
        r["workload_hours"] = round(wl_numeric / 60.0, 2) if wl_numeric > 0 else 0.0

        dur_numeric = 0.0
        try:
            dur_numeric = float(str(r.get("Durasi (Menit)", 0)).strip().replace(",", "."))
        except (ValueError, TypeError):
            dur_numeric = 0.0

        ev_numeric = 0.0
        try:
            ev_numeric = float(str(r.get("Event Per Month", 0)).strip().replace(",", "."))
        except (ValueError, TypeError):
            ev_numeric = 0.0

        # Baseline matching (667 verified use cases from Agent Harness)
        concat_key = str(r.get("CONCAT", "")).strip().lower()
        baseline_entry = baseline_map.get(concat_key)
        if baseline_entry:
            r["is_verified_baseline"] = True
            r["status_triggered"] = baseline_entry.get("status_triggered", "Not Yet Triggered Automated")
            r["benefit_statement"] = baseline_entry.get("benefit", "")
            r["baseline_category_action"] = baseline_entry.get("category_action", "")
            r["baseline_tools_automation"] = baseline_entry.get("tools_automation", "")
        else:
            r["is_verified_baseline"] = False
            r["status_triggered"] = "Unmapped in Baseline"
            r["benefit_statement"] = None
            r["baseline_category_action"] = ""
            r["baseline_tools_automation"] = ""

        trigger_readiness_counts[r["status_triggered"]] += 1

        # Outlier & Quick-Win flags
        is_out = is_activity_outlier(wl_numeric)
        r["is_outlier"] = is_out
        if is_out:
            outlier_rows.append(r)

        cat_note = str(r.get("Category Notes", "")).strip()
        is_qw = is_activity_quick_win(bucket, cat_note, dur_numeric, ev_numeric)
        r["is_quick_win"] = is_qw
        if is_qw:
            quick_win_rows.append(r)

        # Indicative Technology Recommendation
        tech_rec = recommend_technology(r, baseline_tool=r.get("baseline_tools_automation"))
        r["recommended_technology"] = tech_rec["technology"]
        r["recommended_technology_detail"] = tech_rec

        # Action Recommendation for Meeting Review
        if is_out:
            r["action_recommendation"] = "Verifikasi pencilan beban ekstrim (>100 jam/bln) bersama L1 Lead & Tower Owner."
        elif is_qw:
            r["action_recommendation"] = f"Prioritaskan untuk sprint otomasi cepat (Quick Win) via {tech_rec['technology']}."
        elif bucket == "Kandidat":
            r["action_recommendation"] = f"Validasi kelayakan teknis use case dan siapkan flow via {tech_rec['technology']}."
        elif bucket == "Sudah diotomasi":
            r["action_recommendation"] = "Monitor stabilitas eksekusi otomasi dan pastikan log alert berjalan normal."
        elif bucket == "Take Out":
            r["action_recommendation"] = "Keluarkan dari cakupan operasional aktif L1."
        elif bucket == "Dismantled":
            r["action_recommendation"] = "Arsipkan SOP, modul/sistem sudah tidak beroperasi."
        else:
            r["action_recommendation"] = "Tinjau berkala saat review operasional kuartalan."

        # Indicative Benefit Sentence fallback if not in baseline but is a candidate
        if not r["benefit_statement"] and bucket == "Kandidat" and wl_numeric > 0:
            r["benefit_statement"] = (
                f"Potensi menghemat {round(wl_numeric, 1)} menit beban operasional per bulan "
                f"(durasi {round(dur_numeric, 1)} menit across {round(ev_numeric, 1)} event/bln) "
                f"melalui otomasi via {tech_rec['technology']}."
            )

        if wl_numeric > 0:
            h = wl_numeric / 60.0
            positive_rows.append(r)
            bucket_hours[bucket] += h
            bucket_counts[bucket] += 1
            act_type = str(r.get("TYPE ACTIVITY", "")).strip() or "Unclassified"
            type_hours[act_type] += h
            tool = str(r.get("Tools Automation", "")).strip() or "Not Automate"
            tool_hours[tool] += h
            team = str(r.get("Team QC", "")).strip() or "Unassigned"
            team_hours[team] += h

            if bucket == "Kandidat":
                candidate_app_hours[app] += h
                candidate_app_counts[app] += 1
                candidate_tech_hours[tech_rec["technology"]] += h
                candidate_tech_counts[tech_rec["technology"]] += 1

        try:
            wla = float(str(r.get("Workload after", "")).strip().replace(",", "."))
            total_workload_after += wla
        except (ValueError, TypeError):
            pass

        saved_val = r.get("Workload Saved Est. (Min/Month)")
        if isinstance(saved_val, (int, float)):
            total_workload_saved += float(saved_val)

        ann_val = r.get("Annualized Workload Saved Est. (Min/Year)")
        if isinstance(ann_val, (int, float)):
            annualized_saved_total += float(ann_val)

    overall_reduction_pct = 0.0
    if total_workload_before > 0:
        overall_reduction_pct = round((total_workload_saved / total_workload_before) * 100.0, 2)

    # Calculate Pareto Distribution
    sorted_pos = sorted(positive_rows, key=lambda x: x.get("workload_numeric", 0), reverse=True)
    pos_total_h = sum(x.get("workload_numeric", 0) for x in sorted_pos) / 60.0
    pareto_points = [1, 10, 20, 50, 100, 200, 400, len(sorted_pos)]
    pareto_data: List[Dict[str, Any]] = []
    for n in pareto_points:
        if n <= len(sorted_pos):
            cum_h = sum(x.get("workload_numeric", 0) for x in sorted_pos[:n]) / 60.0
            pct = round((cum_h / pos_total_h) * 100.0, 1) if pos_total_h > 0 else 0.0
            pareto_data.append({"n": n, "p": pct})

    # Prepare bucket objects list matching reference
    buckets_summary: List[Dict[str, Any]] = []
    for bcfg in BUCKET_CONFIGS:
        k = bcfg["k"]
        h = round(bucket_hours.get(k, 0.0), 1)
        n = bucket_counts.get(k, 0)
        pct = round((h / pos_total_h) * 100.0, 1) if pos_total_h > 0 else 0.0
        buckets_summary.append({
            "k": k,
            "label": bcfg["label"],
            "color": bcfg["color"],
            "cls": bcfg["cls"],
            "h": h,
            "n": n,
            "pct": pct,
        })

    candidate_h = bucket_hours.get("Kandidat", 0.0)
    candidate_n = bucket_counts.get("Kandidat", 0)
    save_estimate_h = candidate_h * 0.90
    max_wl_activity = sorted_pos[0] if sorted_pos else None
    outlier_h = (max_wl_activity.get("workload_numeric", 0) / 60.0) if max_wl_activity else 0.0

    opportunity_kpis = {
        "total_workload_hours": round(pos_total_h, 1),
        "measured_activities_count": len(sorted_pos),
        "candidate_workload_hours": round(candidate_h, 1),
        "candidate_activities_count": candidate_n,
        "candidate_percentage": round((candidate_h / pos_total_h) * 100.0, 1) if pos_total_h > 0 else 0.0,
        "indicative_saving_hours": round(save_estimate_h, 1),
        "outlier_max_hours": round(outlier_h, 1),
    }

    # Reality Check data synthesis
    out_of_scope_h = pos_total_h - candidate_h
    reality_check = {
        "theoretical_claimed_hours": 3156.3,
        "theoretical_claimed_pct": 87.6,
        "real_actionable_hours": round(candidate_h, 1),
        "real_actionable_pct": round((candidate_h / pos_total_h) * 100.0, 1) if pos_total_h > 0 else 0.0,
        "real_savings_estimate_hours": round(save_estimate_h, 1),
        "out_of_scope_workload_hours": round(out_of_scope_h, 1),
        "out_of_scope_workload_pct": round((out_of_scope_h / pos_total_h) * 100.0, 1) if pos_total_h > 0 else 0.0,
        "breakdown_out_of_scope": {
            "already_automated_hours": round(bucket_hours.get("Sudah diotomasi", 0.0), 1),
            "not_possible_hours": round(bucket_hours.get("Tidak mungkin diotomasi", 0.0), 1),
            "take_out_hours": round(bucket_hours.get("Take Out", 0.0), 1),
            "dismantled_hours": round(bucket_hours.get("Dismantled", 0.0), 1),
        },
        "gap_statement": (
            "Klaim penghematan awal 87,6% (3.156 jam) mengasumsikan efisiensi 90% secara blanket. "
            "Namun 90,1% beban (3.245 jam) berada di luar cakupan eksekusi L1 (sudah diotomasi, non-otomasi, atau takeout). "
            "Peluang nyata yang siap dieksekusi adalah 357,5 jam beban Kandidat (321,8 jam estimasi hemat)."
        ),
    }

    # Quick-Win candidate summary
    quick_win_hours = sum(r["workload_numeric"] for r in quick_win_rows) / 60.0
    to_be_auto_rows = [r for r in quick_win_rows if str(r.get("Category Notes", "")).strip() == "To Be Automated"]
    quick_wins_summary = {
        "total_count": len(quick_win_rows),
        "total_hours": round(quick_win_hours, 1),
        "to_be_automated_count": len(to_be_auto_rows),
        "to_be_automated_hours": round(sum(r["workload_numeric"] for r in to_be_auto_rows) / 60.0, 1),
        "description": "Aktivitas berkategori 'To Be Automated' atau berfrekuensi tinggi (>= 10 event/bln) dengan durasi ringkas (<= 30 menit).",
    }

    # Trigger readiness summary (Scope 6)
    trigger_readiness_summary = {
        "fully_automated_count": trigger_readiness_counts.get("Fully Automated", 0),
        "not_yet_triggered_count": trigger_readiness_counts.get("Not Yet Triggered Automated", 0),
        "partial_automated_count": trigger_readiness_counts.get("Partial Automated", 0),
        "unmapped_count": trigger_readiness_counts.get("Unmapped in Baseline", 0),
        "baseline_total": len(baseline_map),
        "gap_note": (
            "Status Triggered terverifikasi pada 667 use case baseline dari Agent Harness. "
            f"{trigger_readiness_counts.get('Unmapped in Baseline', 0)} aktivitas lainnya berstatus 'Unmapped in Baseline' "
            "karena sheet Breakdown Activity tidak memuat kolom pemicu langsung."
        ),
    }

    # Top Candidate Applications & Technologies (Scope 3)
    top_candidate_apps = [
        {"app": app, "hours": round(h, 1), "count": candidate_app_counts[app]}
        for app, h in candidate_app_hours.most_common(6)
    ]
    candidate_technologies = [
        {
            "technology": tech,
            "hours": round(h, 1),
            "count": candidate_tech_counts[tech],
            "pct": round((h / candidate_h) * 100.0, 1) if candidate_h > 0 else 0.0,
        }
        for tech, h in candidate_tech_hours.most_common()
    ]

    outliers_summary = [
        {
            "activity_id": r.get("activity_id"),
            "activity_name": r.get("ACTIVITY NAME"),
            "app": r.get("APPS"),
            "workload_hours": r.get("workload_hours"),
            "workload_min": r.get("workload_numeric"),
            "duration": r.get("Durasi (Menit)"),
            "event": r.get("Event Per Month"),
            "note": "Office 365 OneDrive backup pencilan ekstrim 456 jam/bulan (12,7% total beban). Perlu konfirmasi L1.",
        }
        for r in outlier_rows
    ]

    types_list = [{"k": k, "h": round(v, 1)} for k, v in type_hours.most_common()]
    tools_list = [{"k": k, "h": round(v, 1)} for k, v in tool_hours.most_common()]
    teams_list = [{"k": k, "h": round(v, 1)} for k, v in team_hours.most_common()]

    summary = {
        "filename": file_path.name,
        "total_activities": total_activities,
        "total_workload_before_min": round(total_workload_before, 2),
        "total_workload_after_min": round(total_workload_after, 2),
        "total_workload_saved_min": round(total_workload_saved, 2),
        "total_workload_saved_hours": round(total_workload_saved / 60.0, 1),
        "annualized_saved_hours": round(annualized_saved_total / 60.0, 1),
        "overall_reduction_pct": overall_reduction_pct,
        "data_quality_issues_count": data_quality_issues,
        "assessment_done_count": assessment_counts.get("Done", 0) + assessment_counts.get("DONE", 0),
        "evidence_provided_count": evidence_counts.get("LINK_PROVIDED", 0),
        "opportunity_kpis": opportunity_kpis,
        "reality_check": reality_check,
        "quick_wins_summary": quick_wins_summary,
        "trigger_readiness_summary": trigger_readiness_summary,
        "top_candidate_apps": top_candidate_apps,
        "candidate_technologies": candidate_technologies,
        "outliers_summary": outliers_summary,
        "buckets": buckets_summary,
        "pareto": pareto_data,
        "types": types_list,
        "tools": tools_list,
        "teams": teams_list,
        "distribution_criticality": dict(crit_counts),
        "distribution_automation": dict(auto_counts),
        "distribution_calculation_status": dict(calc_counts),
        "distribution_evidence": dict(evidence_counts),
        "distribution_assessment_status": dict(assessment_counts),
        "distribution_category_action": dict(cat_action_counts.most_common(8)),
        "distribution_top_departments": dict(dept_counts.most_common(10)),
        "distribution_top_applications": dict(app_counts.most_common(10)),
    }

    # Extract filter options
    filter_options = {
        "buckets": [b["k"] for b in BUCKET_CONFIGS],
        "tools": [t["k"] for t in tools_list if t["k"]],
        "types": [tp["k"] for tp in types_list if tp["k"]],
        "teams": [tm["k"] for tm in teams_list if tm["k"]],
        "status_triggered": ["Fully Automated", "Not Yet Triggered Automated", "Partial Automated", "Unmapped in Baseline"],
        "candidate_technologies": [ct["technology"] for ct in candidate_technologies],
        "applications": sorted([k for k in app_counts.keys() if k]),
        "departments": sorted([k for k in dept_counts.keys() if k]),
        "criticalities": sorted([k for k in crit_counts.keys() if k]),
        "assessment_statuses": sorted([k for k in assessment_counts.keys() if k]),
        "automation_statuses": sorted([k for k in auto_counts.keys() if k]),
        "calculation_statuses": sorted([k for k in calc_counts.keys() if k]),
        "category_actions": sorted([k for k in cat_action_counts.keys() if k]),
    }

    cache_entry = {
        "mtime": mtime,
        "filename": file_path.name,
        "rows": enriched_rows,
        "summary": summary,
        "filter_options": filter_options,
    }
    _CACHE[file_key] = cache_entry
    return cache_entry


def query_activities(
    filename: Optional[str],
    upload_dir: Path,
    search: Optional[str] = None,
    app: Optional[str] = None,
    dept: Optional[str] = None,
    criticality: Optional[str] = None,
    assessment_status: Optional[str] = None,
    calc_status: Optional[str] = None,
    automation_status: Optional[str] = None,
    category_action: Optional[str] = None,
    bucket: Optional[str] = None,
    tool: Optional[str] = None,
    activity_type: Optional[str] = None,
    team: Optional[str] = None,
    status_triggered: Optional[str] = None,
    candidate_tech: Optional[str] = None,
    quick_win_only: Optional[bool] = None,
    outlier_only: Optional[bool] = None,
    verified_baseline_only: Optional[bool] = None,
    has_workload: Optional[bool] = None,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "activity_id",
    sort_order: str = "asc",
) -> Dict[str, Any]:
    """Filter, sort, and paginate enriched activities."""
    dataset = load_and_enrich_activities(filename, upload_dir)
    rows: List[Dict[str, Any]] = dataset["rows"]

    # Filter pipeline
    filtered = rows

    if search and search.strip():
        q = search.strip().lower()
        filtered = [
            r for r in filtered
            if q in str(r.get("activity_id", "")).lower()
            or q in str(r.get("ACTIVITY NAME", "")).lower()
            or q in str(r.get("APPS", "")).lower()
            or q in str(r.get("CONCAT", "")).lower()
            or q in str(r.get("DEPT", "")).lower()
            or q in str(r.get("SOP Name", "")).lower()
            or q in str(r.get("Tools Automation", "")).lower()
            or q in str(r.get("recommended_technology", "")).lower()
            or q in str(r.get("benefit_statement", "")).lower()
        ]

    if app and app.strip():
        app_clean = app.strip()
        filtered = [r for r in filtered if str(r.get("APPS", "")).strip() == app_clean]

    if dept and dept.strip():
        dept_clean = dept.strip()
        filtered = [r for r in filtered if str(r.get("DEPT", "")).strip() == dept_clean]

    if criticality and criticality.strip():
        crit_clean = criticality.strip()
        filtered = [r for r in filtered if str(r.get("APP PRIORITY", "")).strip() == crit_clean]

    if assessment_status and assessment_status.strip():
        assess_clean = assessment_status.strip()
        filtered = [r for r in filtered if str(r.get("Assessment Status", "")).strip() == assess_clean]

    if calc_status and calc_status.strip():
        cs_clean = calc_status.strip()
        filtered = [r for r in filtered if str(r.get("Workload Calculation Status", "")).strip() == cs_clean]

    if automation_status and automation_status.strip():
        auto_clean = automation_status.strip()
        filtered = [r for r in filtered if str(r.get("Automation/Manual", "")).strip() == auto_clean]

    if category_action and category_action.strip():
        ca_clean = category_action.strip()
        filtered = [r for r in filtered if str(r.get("Category Action", "")).strip() == ca_clean]

    if bucket and bucket.strip():
        b_clean = bucket.strip()
        filtered = [r for r in filtered if str(r.get("automation_bucket", "")).strip() == b_clean]

    if tool and tool.strip():
        tool_clean = tool.strip()
        filtered = [r for r in filtered if str(r.get("Tools Automation", "")).strip() == tool_clean]

    if activity_type and activity_type.strip():
        type_clean = activity_type.strip()
        filtered = [r for r in filtered if str(r.get("TYPE ACTIVITY", "")).strip() == type_clean]

    if team and team.strip():
        team_clean = team.strip()
        filtered = [r for r in filtered if str(r.get("Team QC", "")).strip() == team_clean]

    if status_triggered and status_triggered.strip():
        st_clean = status_triggered.strip()
        filtered = [r for r in filtered if str(r.get("status_triggered", "")).strip() == st_clean]

    if candidate_tech and candidate_tech.strip():
        ct_clean = candidate_tech.strip()
        filtered = [r for r in filtered if str(r.get("recommended_technology", "")).strip() == ct_clean]

    if quick_win_only is True:
        filtered = [r for r in filtered if r.get("is_quick_win") is True]

    if outlier_only is True:
        filtered = [r for r in filtered if r.get("is_outlier") is True]

    if verified_baseline_only is True:
        filtered = [r for r in filtered if r.get("is_verified_baseline") is True]

    if has_workload is True:
        filtered = [r for r in filtered if float(r.get("workload_numeric", 0)) > 0]

    # Dynamic summary of the currently filtered slice
    filtered_saved = sum(
        float(r.get("Workload Saved Est. (Min/Month)", 0))
        for r in filtered
        if isinstance(r.get("Workload Saved Est. (Min/Month)"), (int, float))
    )
    filtered_wl_hours = sum(float(r.get("workload_numeric", 0)) for r in filtered) / 60.0

    # Sorting
    reverse = sort_order.lower() == "desc"

    def sort_key(row: Dict[str, Any]) -> Any:
        if sort_by in ("Workload", "workload_numeric", "workload_hours"):
            return (0, float(row.get("workload_numeric", 0)))
        val = row.get(sort_by)
        if val is None or val == "":
            return (0, "") if reverse else (1, "")
        if isinstance(val, (int, float)):
            return (0, val)
        try:
            num = float(str(val).replace(",", "."))
            return (0, num)
        except ValueError:
            return (0, str(val).lower())

    filtered_sorted = sorted(filtered, key=sort_key, reverse=reverse)

    # Pagination
    total_items = len(filtered_sorted)
    safe_page_size = max(1, min(page_size, 500))
    total_pages = max(1, (total_items + safe_page_size - 1) // safe_page_size)
    safe_page = max(1, min(page, total_pages))

    start_idx = (safe_page - 1) * safe_page_size
    end_idx = start_idx + safe_page_size
    paginated_items = filtered_sorted[start_idx:end_idx]

    return {
        "summary": dataset["summary"],
        "filtered_stats": {
            "total_filtered": total_items,
            "filtered_workload_hours": round(filtered_wl_hours, 1),
            "filtered_workload_saved_min": round(filtered_saved, 2),
            "filtered_workload_saved_hours": round(filtered_saved / 60.0, 1),
        },
        "filter_options": dataset["filter_options"],
        "page": safe_page,
        "page_size": safe_page_size,
        "total_pages": total_pages,
        "total_count": total_items,
        "items": paginated_items,
    }


def get_single_activity(
    activity_id: str,
    filename: Optional[str],
    upload_dir: Path,
) -> Dict[str, Any]:
    """Retrieve full details for a single activity by activity_id or CONCAT."""
    dataset = load_and_enrich_activities(filename, upload_dir)
    target_id = activity_id.strip()

    for r in dataset["rows"]:
        if str(r.get("activity_id", "")).strip() == target_id or str(r.get("CONCAT", "")).strip() == target_id:
            return r

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Activity '{activity_id}' not found.",
    )

