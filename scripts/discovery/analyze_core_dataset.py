"""Comprehensive Core Dataset Analysis Script.

Deep statistical profiling, data quality audit, and cross-column relationship mapping
for breakdown_activity_261105_1704_1.json (3,460 records).
"""

import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_FILE = Path(r"backend/uploads/breakdown_activity_261105_1704_1.json")
OUTPUT_JSON = Path(r"scripts/discovery/core_dataset_analysis_results.json")
CHUNK_SIZE = 500

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def clean_val(val):
    if val is None:
        return None
    s = str(val).strip()
    return s if s != "" else None

def parse_num(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None

def run_analysis():
    print(f"Reading {SOURCE_FILE}...")
    sha256 = compute_sha256(SOURCE_FILE)
    file_size_bytes = SOURCE_FILE.stat().st_size
    
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    records = raw_data.get("value", [])
    total_records = len(records)
    print(f"Loaded {total_records} records.")
    
    # 1. Chunking validation
    chunks = []
    chunk_summaries = []
    processed_count = 0
    all_seen_indices = set()
    
    for i in range(0, total_records, CHUNK_SIZE):
        chunk_slice = records[i:i + CHUNK_SIZE]
        chunk_len = len(chunk_slice)
        chunk_indices = set(range(i, i + chunk_len))
        
        # Verify no overlapping indices
        overlap = all_seen_indices.intersection(chunk_indices)
        assert len(overlap) == 0, f"Overlapping indices detected in chunk {len(chunks)}!"
        all_seen_indices.update(chunk_indices)
        
        chunks.append(chunk_slice)
        chunk_summaries.append({
            "chunk_index": len(chunks) - 1,
            "start_idx": i,
            "end_idx": i + chunk_len - 1,
            "record_count": chunk_len
        })
        processed_count += chunk_len
    
    assert processed_count == total_records, f"Mismatch: processed {processed_count} != total {total_records}"
    assert len(all_seen_indices) == total_records, "Some record indices were missed!"
    print(f"Successfully chunked into {len(chunks)} chunks with 100% reconciliation.")

    # 2. Extract column list
    all_columns = list(records[0].keys())
    
    # Data structure dictionary
    field_metadata = {
        "activity_id": {"role": "Primary Key", "desc": "Identifier unik aktivitas, identik dengan CONCAT"},
        "APPS": {"role": "Application Key", "desc": "Nama aplikasi sistem, kunci relasi ke metadata aplikasi"},
        "ACTIVITY NAME": {"role": "Core Dimension", "desc": "Nama spesifik aktivitas operasional L1"},
        "TYPE ACTIVITY": {"role": "Category Dimension", "desc": "Klasifikasi jenis aktivitas awal (sumber manual)"},
        "Workload": {"role": "Derived Metric", "desc": "Beban kerja bulanan dalam menit-orang (Durasi × Event Per Month)"},
        "Workload after": {"role": "Derived Metric", "desc": "Beban kerja bulanan setelah otomasi/improvement (Durasi after × Event)"},
        "Link Confluence": {"role": "Documentation Link", "desc": "Tautan ke SOP / Runbook di Confluence Telkomsel"},
        "Link Wiki": {"role": "Documentation Link", "desc": "Tautan wiki dokumentasi (seluruh baris kosong)"},
        "Improvement Category": {"role": "Improvement Dimension", "desc": "Kategori rencana improvement (misal: As Is, Automation)"},
        "Category Notes": {"role": "Improvement Dimension", "desc": "Catatan kategori tindakan (misal: As Is, To Be Automated)"},
        "Action by": {"role": "Operational Role", "desc": "Pelaksana aktivitas operasional (misal: L1, Vendor)"},
        "New Improvement Category Fixed": {"role": "Standardized Dimension", "desc": "Kategori improvement yang telah distandardisasi/dibersihkan"},
        "Additional Notes": {"role": "Free-text Note", "desc": "Catatan tambahan terkait verifikasi/kondisi aktivitas"},
        "DIV": {"role": "Organizational Lookup", "desc": "Divisi pemilik aplikasi (hasil lookup via APPS)"},
        "CONCAT": {"role": "Composite Key", "desc": "Penggabungan APPS - ACTIVITY NAME"},
        "DEPT": {"role": "Organizational Lookup", "desc": "Departemen pemilik aplikasi (hasil lookup via APPS)"},
        "APP PRIORITY": {"role": "Application Priority", "desc": "Tingkat prioritas aplikasi (misal: Business Critical)"},
        "Number Activity": {"role": "Sequence/Counter", "desc": "Penanda nomor aktivitas (dominan bernilai '1')"},
        "Durasi (Menit)": {"role": "Operational Metric", "desc": "Durasi pengerjaan aktivitas per satu kejadian (menit)"},
        "Event Per Month": {"role": "Operational Frequency", "desc": "Frekuensi kemunculan aktivitas dalam satu bulan"},
        "Durasi after": {"role": "Operational Metric", "desc": "Estimasi durasi pengerjaan setelah otomasi (menit)"},
        "Automation/Manual": {"role": "Operational Mode", "desc": "Mode eksekusi aktivitas (Manual vs Automated)"},
        "FMC/Mobile": {"role": "Business Domain", "desc": "Domain layanan bisnis (Mobile vs FMC, hasil lookup SOP)"},
        "Team QC": {"role": "Quality Control", "desc": "Tim Quality Control yang mereview SOP (hasil lookup APPS)"},
        "SOP Name": {"role": "Documentation Title", "desc": "Judul dokumen SOP terkait"},
        "Status": {"role": "Operational Status", "desc": "Status kesiapan SOP operasional (misal: DONE, Takeout)"},
        "Status (Old)": {"role": "Historical Status", "desc": "Status historis sebelum pembaruan evaluasi"},
        "TYPE ACTIVITY2": {"role": "Standardized Category", "desc": "Kategori aktivitas terstandarisasi via formula IFS"},
        "Assessment Status": {"role": "Governance Status", "desc": "Status peninjauan asesmen (Done vs empty)"},
        "Tools": {"role": "Technical Environment", "desc": "Klasifikasi alat/lingkungan teknis (OS, DB, Web, dll)"},
        "Category Action": {"role": "Improvement Action", "desc": "Aksi spesifik perbaikan (seluruh baris kosong di JSON sumber)"},
        "Confirmation Tower/L2": {"role": "Governance Alignment", "desc": "Status konfirmasi tim teknis Tower / L2"},
        "Support Needed": {"role": "Dependency / Enabler", "desc": "Dukungan atau dependensi yang dibutuhkan"},
        "Phase": {"role": "Implementation Phase", "desc": "Fase implementasi automasi (misal: Phase 1, Phase 2)"},
        "Ops Activity": {"role": "Operational Tag", "desc": "Tag operasional aktivitas"},
        "Tools Automation": {"role": "Automation Tooling", "desc": "Alat automasi yang direncanakan / Not Automate"},
        "Module AO": {"role": "Module Identifier", "desc": "Modul Automation Opportunity terkait"}
    }
    
    col_profiles = {}
    
    for col in all_columns:
        vals = [r.get(col) for r in records]
        
        # Null vs empty string
        null_count = sum(1 for v in vals if v is None)
        empty_str_count = sum(1 for v in vals if isinstance(v, str) and v.strip() == "")
        total_missing = null_count + empty_str_count
        missing_pct = round((total_missing / total_records) * 100, 2)
        filled_count = total_records - total_missing
        filled_pct = round((filled_count / total_records) * 100, 2)
        
        # Types observed
        types_observed = sorted(list(set(type(v).__name__ for v in vals)))
        
        # Clean non-empty values
        clean_vals = [clean_val(v) for v in vals if clean_val(v) is not None]
        unique_vals = sorted(list(set(clean_vals)))
        unique_count = len(unique_vals)
        
        # Samples
        samples = clean_vals[:5] if clean_vals else []
        
        # Frequency distribution (Top 10)
        c = Counter(clean_vals)
        top_cats = [{"value": k, "count": count, "pct": round(count / total_records * 100, 2)} for k, count in c.most_common(10)]
        
        # Numeric parsing
        parsed_nums = [parse_num(v) for v in clean_vals]
        valid_nums = [n for n in parsed_nums if n is not None]
        is_num_col = (len(valid_nums) > 0) and (len(valid_nums) >= filled_count * 0.8)
        
        num_stats = None
        if is_num_col and valid_nums:
            arr = np.array(valid_nums, dtype=float)
            num_stats = {
                "count_numeric": len(arr),
                "non_numeric_count": filled_count - len(arr),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "mean": round(float(np.mean(arr)), 4),
                "median": round(float(np.median(arr)), 4),
                "std": round(float(np.std(arr)), 4),
                "q25": round(float(np.percentile(arr, 25)), 4),
                "q75": round(float(np.percentile(arr, 75)), 4),
                "iqr": round(float(np.percentile(arr, 75) - np.percentile(arr, 25)), 4),
                "zero_count": int(np.sum(arr == 0)),
                "negative_count": int(np.sum(arr < 0))
            }
            
        col_profiles[col] = {
            "name": col,
            "role": field_metadata.get(col, {}).get("role", "UNKNOWN"),
            "description": field_metadata.get(col, {}).get("desc", "UNKNOWN"),
            "types_observed": types_observed,
            "total_records": total_records,
            "null_count": null_count,
            "empty_str_count": empty_str_count,
            "missing_count": total_missing,
            "missing_pct": missing_pct,
            "filled_count": filled_count,
            "filled_pct": filled_pct,
            "unique_count": unique_count,
            "samples": samples,
            "is_numeric": is_num_col,
            "numeric_stats": num_stats,
            "top_categories": top_cats
        }
        
    # 3. Data Quality Checks
    # Exact duplicate records
    seen_records = set()
    dup_record_count = 0
    for r in records:
        r_str = json.dumps(r, sort_keys=True)
        if r_str in seen_records:
            dup_record_count += 1
        seen_records.add(r_str)
        
    # activity_id analysis
    aids = [clean_val(r.get("activity_id")) for r in records]
    aid_counter = Counter(aids)
    missing_aids = sum(1 for a in aids if a is None)
    dup_aids = {k: v for k, v in aid_counter.items() if v > 1 and k is not None}
    
    # CONCAT analysis
    concats = [clean_val(r.get("CONCAT")) for r in records]
    concat_counter = Counter(concats)
    missing_concats = sum(1 for c in concats if c is None)
    dup_concats = {k: v for k, v in concat_counter.items() if v > 1 and k is not None}
    
    # Check identity: activity_id == CONCAT == f"{APPS} - {ACTIVITY NAME}"
    id_equals_concat = sum(1 for r in records if clean_val(r.get("activity_id")) == clean_val(r.get("CONCAT")))
    concat_equals_composed = sum(1 for r in records if clean_val(r.get("CONCAT")) == f"{clean_val(r.get('APPS'))} - {clean_val(r.get('ACTIVITY NAME'))}")

    # Non-numeric string anomalies in numeric fields
    non_numeric_anomalies = {
        "Durasi (Menit)": Counter(),
        "Event Per Month": Counter()
    }
    for r in records:
        dur = clean_val(r.get("Durasi (Menit)"))
        if dur and parse_num(dur) is None:
            non_numeric_anomalies["Durasi (Menit)"][dur] += 1
            
        ev = clean_val(r.get("Event Per Month"))
        if ev and parse_num(ev) is None:
            non_numeric_anomalies["Event Per Month"][ev] += 1

    # URL audits
    def analyze_urls(col):
        raw_vals = [clean_val(r.get(col)) for r in records if clean_val(r.get(col)) is not None]
        valid_http = []
        text_non_http = []
        domains = Counter()
        for u in raw_vals:
            if u.startswith("http://") or u.startswith("https://"):
                valid_http.append(u)
                domain = u.split("://")[1].split("/")[0]
                domains[domain] += 1
            else:
                text_non_http.append(u)
        return {
            "total_populated": len(raw_vals),
            "valid_http_count": len(valid_http),
            "valid_http_pct": round(len(valid_http) / total_records * 100, 2),
            "text_notes_count": len(text_non_http),
            "text_notes_samples": text_non_http[:5],
            "domain_breakdown": dict(domains.most_common())
        }
    
    confluence_audit = analyze_urls("Link Confluence")
    wiki_audit = analyze_urls("Link Wiki")

    # 4. Formula Verification
    # Formula 1: Workload = Durasi (Menit) * Event Per Month
    f1_valid = 0
    f1_match = 0
    f1_mismatches = []
    
    # Formula 2: Workload after = Durasi after * Event Per Month
    f2_valid = 0
    f2_match = 0
    f2_mismatches = []
    
    # Formula 3: Durasi after == Durasi * 0.1
    f3_exact_10pct = 0
    f3_zero = 0
    f3_other = 0
    f3_missing = 0
    
    # Missing operand combinations
    operand_combos = Counter()
    
    for idx, r in enumerate(records):
        dur = parse_num(r.get("Durasi (Menit)"))
        ev = parse_num(r.get("Event Per Month"))
        wl = parse_num(r.get("Workload"))
        dur_after = parse_num(r.get("Durasi after"))
        wl_after = parse_num(r.get("Workload after"))
        
        has_dur = dur is not None
        has_ev = ev is not None
        has_wl = wl is not None
        operand_combos[(has_dur, has_ev, has_wl)] += 1
        
        if has_dur and has_ev and has_wl:
            f1_valid += 1
            exp_wl = dur * ev
            if math.isclose(wl, exp_wl, rel_tol=1e-3, abs_tol=1e-2):
                f1_match += 1
            else:
                f1_mismatches.append({"idx": idx, "aid": r.get("activity_id"), "dur": dur, "ev": ev, "wl": wl, "exp": exp_wl})
                
        if dur_after is not None and has_ev and wl_after is not None:
            f2_valid += 1
            exp_wl_after = dur_after * ev
            if math.isclose(wl_after, exp_wl_after, rel_tol=1e-3, abs_tol=1e-2):
                f2_match += 1
            else:
                f2_mismatches.append({"idx": idx, "aid": r.get("activity_id"), "dur_after": dur_after, "ev": ev, "wl_after": wl_after, "exp": exp_wl_after})
                
        if has_dur and dur_after is not None:
            if dur_after == 0:
                f3_zero += 1
            elif math.isclose(dur_after, dur * 0.1, rel_tol=1e-3, abs_tol=1e-2):
                f3_exact_10pct += 1
            else:
                f3_other += 1
        else:
            f3_missing += 1

    # 5. Cross-Column & Correlations
    df = pd.DataFrame(records)
    
    # Numerics
    df["num_dur"] = [parse_num(r.get("Durasi (Menit)")) for r in records]
    df["num_ev"] = [parse_num(r.get("Event Per Month")) for r in records]
    df["num_wl"] = [parse_num(r.get("Workload")) for r in records]
    df["num_dur_after"] = [parse_num(r.get("Durasi after")) for r in records]
    df["num_wl_after"] = [parse_num(r.get("Workload after")) for r in records]
    df["num_wl_saved"] = df["num_wl"] - df["num_wl_after"]
    
    num_subset = df[["num_dur", "num_ev", "num_wl", "num_dur_after", "num_wl_after", "num_wl_saved"]].dropna()
    
    pearson = num_subset.corr(method="pearson").round(4).to_dict()
    spearman = num_subset.corr(method="spearman").round(4).to_dict()
    
    # Status by Top Apps
    top_apps = [k for k, v in Counter(df["APPS"].dropna()).most_common(10) if k.strip()]
    top_statuses = [k for k, v in Counter(df["Status"].dropna()).most_common(5) if k.strip()]
    status_by_app = pd.crosstab(df["APPS"], df["Status"]).reindex(index=top_apps, columns=top_statuses, fill_value=0).to_dict()
    
    # Tools by Top Apps
    top_tools = [k for k, v in Counter(df["Tools"].dropna()).most_common(5) if k.strip()]
    tools_by_app = pd.crosstab(df["APPS"], df["Tools"]).reindex(index=top_apps, columns=top_tools, fill_value=0).to_dict()
    
    # DIV and DEPT distribution
    div_dist = [{"div": k, "count": v, "pct": round(v / total_records * 100, 2)} for k, v in Counter(df["DIV"].dropna()).most_common(10)]
    dept_dist = [{"dept": k, "count": v, "pct": round(v / total_records * 100, 2)} for k, v in Counter(df["DEPT"].dropna()).most_common(10)]
    
    # Status consistency: Status vs Assessment Status vs Status (Old)
    status_cross = pd.crosstab(df["Status"].fillna("[EMPTY]"), df["Assessment Status"].fillna("[EMPTY]")).to_dict()
    
    # 6. Activity Characteristics & Top 10 Records
    def extract_top(sort_col, n=10):
        sorted_df = df.sort_values(by=sort_col, ascending=False).head(n)
        cols_to_keep = ["activity_id", "APPS", "ACTIVITY NAME", "Durasi (Menit)", "Event Per Month", "Workload", "Durasi after", "Workload after", "Status", "Tools"]
        res = []
        for _, row in sorted_df.iterrows():
            item = {c: row[c] for c in cols_to_keep}
            item["parsed_" + sort_col] = float(row[sort_col])
            res.append(item)
        return res

    top_workload = extract_top("num_wl", 10)
    top_duration = extract_top("num_dur", 10)
    top_events = extract_top("num_ev", 10)
    top_saved = extract_top("num_wl_saved", 10)

    # Workload Clusters / Distribution Bins
    wl_clean = df["num_wl"].dropna()
    wl_bins = {
        "Zero (0)": int((wl_clean == 0).sum()),
        "Micro (1 - 60 min/mo)": int(((wl_clean > 0) & (wl_clean <= 60)).sum()),
        "Low (61 - 300 min/mo)": int(((wl_clean > 60) & (wl_clean <= 300)).sum()),
        "Medium (301 - 1,200 min/mo)": int(((wl_clean > 300) & (wl_clean <= 1200)).sum()),
        "High (1,201 - 6,000 min/mo)": int(((wl_clean > 1200) & (wl_clean <= 6000)).sum()),
        "Critical / Outlier (> 6,000 min/mo)": int((wl_clean > 6000).sum())
    }
    
    # Duration Bins
    dur_clean = df["num_dur"].dropna()
    dur_bins = {
        "Micro (<= 5 min)": int((dur_clean <= 5).sum()),
        "Standard (6 - 30 min)": int(((dur_clean > 5) & (dur_clean <= 30)).sum()),
        "Extended (31 - 60 min)": int(((dur_clean > 30) & (dur_clean <= 60)).sum()),
        "Long (61 - 240 min)": int(((dur_clean > 60) & (dur_clean <= 240)).sum()),
        "Extreme (> 240 min / 4 hrs)": int((dur_clean > 240).sum())
    }

    # Event Frequency Bins
    ev_clean = df["num_ev"].dropna()
    ev_bins = {
        "Sub-monthly (< 1 event/mo)": int(((ev_clean > 0) & (ev_clean < 1)).sum()),
        "Monthly (1 event/mo)": int((ev_clean == 1).sum()),
        "Low (2 - 10 events/mo)": int(((ev_clean > 1) & (ev_clean <= 10)).sum()),
        "Daily Routine (11 - 31 events/mo)": int(((ev_clean > 10) & (ev_clean <= 31)).sum()),
        "High Frequency (32 - 100 events/mo)": int(((ev_clean > 31) & (ev_clean <= 100)).sum()),
        "Intensive (> 100 events/mo)": int((ev_clean > 100).sum())
    }

    results = {
        "metadata": {
            "source_workbook": raw_data.get("source_workbook"),
            "sheet_name": raw_data.get("sheet_name"),
            "extracted_at": raw_data.get("extracted_at"),
            "total_rows_meta": raw_data.get("total_rows"),
            "columns_detected_meta": raw_data.get("columns_detected"),
            "file_size_bytes": file_size_bytes,
            "sha256": sha256,
            "total_records_processed": total_records,
            "total_columns": len(all_columns),
        },
        "chunks": chunk_summaries,
        "column_profiles": col_profiles,
        "data_quality": {
            "exact_duplicate_records": dup_record_count,
            "activity_id_integrity": {
                "missing": missing_aids,
                "unique": len(set(aids)),
                "duplicate_count": len(dup_aids),
                "equals_concat_count": id_equals_concat,
                "equals_concat_pct": round(id_equals_concat / total_records * 100, 2)
            },
            "concat_integrity": {
                "missing": missing_concats,
                "unique": len(set(concats)),
                "duplicate_count": len(dup_concats),
                "equals_composed_count": concat_equals_composed,
                "equals_composed_pct": round(concat_equals_composed / total_records * 100, 2)
            },
            "non_numeric_anomalies": {
                "Durasi (Menit)": dict(non_numeric_anomalies["Durasi (Menit)"]),
                "Event Per Month": dict(non_numeric_anomalies["Event Per Month"])
            },
            "url_audits": {
                "link_confluence": confluence_audit,
                "link_wiki": wiki_audit
            }
        },
        "formula_verification": {
            "workload_formula": {
                "formula": "Workload = Durasi (Menit) * Event Per Month",
                "valid_operands_count": f1_valid,
                "exact_matches_count": f1_match,
                "exact_matches_pct": round(f1_match / f1_valid * 100, 2) if f1_valid else 0,
                "mismatches_count": len(f1_mismatches),
                "mismatches": f1_mismatches
            },
            "workload_after_formula": {
                "formula": "Workload after = Durasi after * Event Per Month",
                "valid_operands_count": f2_valid,
                "exact_matches_count": f2_match,
                "exact_matches_pct": round(f2_match / f2_valid * 100, 2) if f2_valid else 0,
                "mismatches_count": len(f2_mismatches),
                "mismatches": f2_mismatches
            },
            "ten_percent_duration_rule": {
                "rule": "Durasi after = Durasi (Menit) * 0.1",
                "exact_10_percent_count": f3_exact_10pct,
                "exact_10_percent_pct": round(f3_exact_10pct / total_records * 100, 2),
                "zero_duration_after_count": f3_zero,
                "other_ratio_count": f3_other,
                "missing_count": f3_missing
            },
            "operand_combinations": {str(k): v for k, v in operand_combos.items()}
        },
        "statistical_profiling": {
            "workload_bins": wl_bins,
            "duration_bins": dur_bins,
            "event_frequency_bins": ev_bins,
            "correlations": {
                "pearson": pearson,
                "spearman": spearman
            }
        },
        "cross_column": {
            "top_apps": top_apps,
            "status_by_app": status_by_app,
            "tools_by_app": tools_by_app,
            "div_distribution": div_dist,
            "dept_distribution": dept_dist,
            "status_cross_assessment": status_cross
        },
        "activity_characteristics": {
            "top_workload": top_workload,
            "top_duration": top_duration,
            "top_events": top_events,
            "top_saved": top_saved
        }
    }
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"Comprehensive analysis written to {OUTPUT_JSON}!")

if __name__ == "__main__":
    run_analysis()
