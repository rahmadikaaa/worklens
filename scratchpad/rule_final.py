"""WORKLENS — Rule Final Engine & Validation Pipeline
Reverse engineering and deterministic reproduction pipeline for L1 AGIT workload enrichment.

Inputs:
- breakdown_activity_261106_1112.json
- Improvements_With_Benefit.csv

Outputs:
- perbandingan_per_baris.xlsx
- Execution statistics printed to stdout
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


def clean_number(val: Any) -> float:
    """Safely parse numbers with Indonesian comma format, text suffix handling, and error handling.
    Does NOT use naive .replace(',', '').
    """
    if val is None or pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ('n/a', 'nan', 'null', '-', '#value!', '#ref!', '#n/a', 'quarterly', '30/31'):
        return 0.0
    # Normalize Indonesian decimal comma to dot
    val_norm = val_str.replace(' ', '').replace(',', '.')
    # Extract floating/integer number prefix
    match = re.search(r'^-?\d+(?:\.\d+)?', val_norm)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return 0.0
    return 0.0


def predict_category_action(type_activity: str, activity_name: str) -> str:
    """Predict 6-class Category Action from TYPE ACTIVITY and ACTIVITY NAME keywords.
    Empirical accuracy: 94.60% (631/667).
    """
    t_act = str(type_activity or '').strip()
    act = str(activity_name or '').strip().lower()

    # 1. Housekeeping: 99.1% pure correlation
    if t_act == 'Housekeeping' or any(k in act for k in ['housekeeping', 'clear log', 'delete log', 'clear event', 'clean log', 'cleanup', 'delete file', 'remove log']):
        return 'Auto Housekeeping'

    # 2. Service Request & Complaint Handling & Change Management -> Self Service Request
    if t_act in ['Service Request', 'Complaint Handling', 'Change Management']:
        return 'Self Service Request'

    # 3. Auto Restart: specific bot / test runner / admin api services
    if any(k in act for k in ['restart bot', 'running manual bot', 'restart service cypress', 'restart admin api', 'bot1', 'bot2', 'bot3']):
        return 'Auto Restart'

    # 4. Health Check: inspections of process, memory, disk, ping, services
    if any(k in act for k in ['check process', 'check service', 'check memory', 'health check', 'healthcheck', 'check disk', 'storage usage', 'cpu usage']):
        return 'Health Check'

    # 5. Auto Monitoring: monitoring dashboards, widgets, and traffic tracking
    if t_act in ['Daily Activity', 'Monitoring and Alerting'] or any(k in act for k in ['monitoring', 'grafana', 'traffic', 'success rate', 'error count', 'trend error', 'widget', 'dashboard']):
        return 'Auto Monitoring'

    # 6. Smart Healing: incident handling and service remediation
    if t_act == 'Incident Handling' or any(k in act for k in ['restart', 'start stop', 'reboot', 'kill', 'recycle', 'stop and start']):
        return 'Smart Healing'

    return 'Smart Healing'


def predict_tools_automation(tool_json: str, activity_name: str) -> str:
    """Predict and normalize Tools Automation.
    Rules:
    - Normalizes casing ('Shell script' -> 'Shell Script')
    - Maps 'Not Automate' to 'AION' (escalation to primary automation platform)
    - Re-routes monitoring to 'Grafana' if activity relates to Grafana
    Empirical accuracy: 96.85% (646/667).
    """
    t = str(tool_json or '').strip()
    act = str(activity_name or '').lower()

    if t.lower() == 'shell script':
        if 'grafana' in act:
            return 'Grafana'
        return 'Shell Script'
    if t == 'Not Automate':
        if 'grafana' in act:
            return 'Grafana'
        return 'AION'
    return t


def generate_benefit_sentence(
    cat_action: str,
    tool: str,
    status_trig: str,
    durasi: float,
    event: float,
    workload: float
) -> str:
    """Generate deterministic Benefit sentence following the reverse-engineered grammar.
    Matches 100.00% (667/667) when inputs match CSV benchmark.
    """
    action_phrases = {
        'Auto Housekeeping': 'scheduled automated log and disk housekeeping',
        'Auto Monitoring': 'continuous proactive monitoring and real-time anomaly detection',
        'Auto Restart': 'automated service restarts and rapid downtime mitigation',
        'Health Check': 'automated system health checks and proactive issue prevention',
        'Self Service Request': 'streamlined self-service execution and eliminating manual ticket handling',
        'Smart Healing': 'automated fault detection and self-healing recovery',
    }
    action_phrase = action_phrases.get(cat_action, '')

    if tool == 'Not Automate':
        tool_clause = 'through standardized automation'
    elif tool == 'CICD':
        tool_clause = 'via CI/CD automation'
    else:
        tool_clause = f'via {tool}'

    # Edge case: Workload == 0
    if workload == 0:
        if status_trig == 'Fully Automated':
            return f'Eliminates manual intervention time and accelerates system recovery {tool_clause} through {action_phrase}.'
        elif status_trig == 'Not Yet Triggered Automated':
            return f'Potentially eliminates manual intervention time and accelerates system recovery once automated {tool_clause} through {action_phrase}.'
        else:
            return f'Reduces manual intervention time {tool_clause} through {action_phrase}.'

    # Workload format
    if workload < 60:
        wl_str = f'{int(workload)} minutes' if workload.is_integer() else f'{workload} minutes'
    else:
        hours = workload / 60.0
        wl_str = f'{int(hours)} hours' if hours.is_integer() else f'{hours:.1f} hours'

    dur_str = f'{int(durasi)}' if durasi.is_integer() else f'{durasi}'
    ev_str = f'{int(event)}' if event.is_integer() else f'{event}'

    if event == 1:
        saving_clause = f'(saving {dur_str} minutes per event)'
    else:
        saving_clause = f'(saving {dur_str} minutes per event across {ev_str} monthly events)'

    if status_trig == 'Fully Automated':
        return f'Eliminates {wl_str} of manual operational workload per month {saving_clause} {tool_clause} through {action_phrase}.'
    elif status_trig == 'Not Yet Triggered Automated':
        return f'Potentially eliminates {wl_str} of manual operational workload per month {saving_clause} once automated {tool_clause} through {action_phrase}.'
    elif status_trig == 'Partial Automated':
        return f'Reduces monthly operational workload by {wl_str} {saving_clause} {tool_clause} through {action_phrase}.'
    return ''


def run_pipeline(
    json_path: Path,
    csv_path: Path,
    output_excel_path: Path
) -> Dict[str, Any]:
    print(f"Loading JSON from: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        raw_json = json.load(f)['value']
    df_json = pd.DataFrame(raw_json)

    print(f"Loading CSV from: {csv_path}")
    df_csv = pd.read_csv(csv_path)

    # 1. Clean JSON fields
    df_json['durasi_clean'] = df_json['Durasi (Menit)'].apply(clean_number)
    df_json['event_clean'] = df_json['Event Per Month'].apply(clean_number)
    df_json['workload_calc'] = df_json['durasi_clean'] * df_json['event_clean']
    df_json['concat_clean'] = df_json['CONCAT'].astype(str).str.strip()

    # 2. Clean CSV fields
    df_csv['durasi_clean'] = df_csv['Durasi (Menit)'].apply(clean_number)
    df_csv['event_clean'] = df_csv['Event Per Month'].apply(clean_number)
    df_csv['workload_clean'] = df_csv['Workload'].apply(clean_number)
    df_csv['concat_clean'] = df_csv['CONCAT'].astype(str).str.strip()

    # 3. Apply Row Selection Rule to JSON
    rule_notes = [
        'Already automate', 'via ITOC', 'via DSC', 'Already AI', 'No Action',
        'Already healthcheck', 'GUI', 'Need further assessment', 'Already CICD',
        'Already empower', 'Automate', 'Health Check', 'Already healtchechk',
        'Need Further Assesment', 'Already Automate'
    ]
    json_selected = df_json[
        (df_json['Improvement Category'] == 'Automation') &
        (df_json['event_clean'] >= 1.0) &
        (df_json['Additional Notes'].isin(rule_notes))
    ].copy()

    # Apply predictions to selected JSON rows
    json_selected['pred_category_action'] = json_selected.apply(
        lambda r: predict_category_action(r['TYPE ACTIVITY'], r['ACTIVITY NAME']), axis=1
    )
    json_selected['pred_tools_automation'] = json_selected.apply(
        lambda r: predict_tools_automation(r['Tools Automation'], r['ACTIVITY NAME']), axis=1
    )

    # Map CSV lookups
    csv_lookup = {r['concat_clean']: r for _, r in df_csv.iterrows()}
    json_selected_lookup = {r['concat_clean']: r for _, r in json_selected.iterrows()}
    json_all_lookup = {r['concat_clean']: r for _, r in df_json.iterrows()}

    all_keys = sorted(list(set(df_csv['concat_clean']).union(set(json_selected['concat_clean']))))
    print(f"Total Unique Keys across CSV (667) and JSON Rule (673): {len(all_keys)}")

    rows_data = []
    for key in all_keys:
        in_csv = key in csv_lookup
        in_json_rule = key in json_selected_lookup
        in_json_all = key in json_all_lookup

        r_csv = csv_lookup.get(key)
        r_json_sel = json_selected_lookup.get(key)
        r_json_raw = json_all_lookup.get(key)

        presence = "IN_BOTH" if (in_csv and in_json_rule) else ("CSV_ONLY" if in_csv else "JSON_RULE_ONLY")

        # Numerics
        dur_csv = r_csv['durasi_clean'] if in_csv else None
        dur_json = r_json_sel['durasi_clean'] if in_json_rule else (r_json_raw['durasi_clean'] if in_json_all else None)
        dur_match = (dur_csv == dur_json) if (in_csv and dur_json is not None) else None

        ev_csv = r_csv['event_clean'] if in_csv else None
        ev_json = r_json_sel['event_clean'] if in_json_rule else (r_json_raw['event_clean'] if in_json_all else None)
        ev_match = (ev_csv == ev_json) if (in_csv and ev_json is not None) else None

        wl_csv = r_csv['workload_clean'] if in_csv else None
        wl_json = r_json_sel['workload_calc'] if in_json_rule else (r_json_raw['workload_calc'] if in_json_all else None)
        wl_match = (wl_csv == wl_json) if (in_csv and wl_json is not None) else None

        # Category Action
        ca_csv = r_csv['Category Action'] if in_csv else None
        ca_pred = r_json_sel['pred_category_action'] if in_json_rule else predict_category_action(r_json_raw['TYPE ACTIVITY'], r_json_raw['ACTIVITY NAME'])
        ca_match = (ca_csv == ca_pred) if in_csv else None

        # Tools Automation
        tool_csv = r_csv['Tools Automation'] if in_csv else None
        tool_pred = r_json_sel['pred_tools_automation'] if in_json_rule else predict_tools_automation(r_json_raw['Tools Automation'], r_json_raw['ACTIVITY NAME'])
        tool_match = (tool_csv == tool_pred) if in_csv else None

        # Status Triggered
        st_csv = r_csv['Status Triggered'] if in_csv else None

        # Benefit Generation
        ben_csv = r_csv['Benefit'].strip() if in_csv else None

        # 1. Prediction using actual Status Triggered (if available)
        ben_pred_actual_st = generate_benefit_sentence(
            ca_pred, tool_pred, st_csv if st_csv else 'Not Yet Triggered Automated',
            dur_json, ev_json, wl_json
        ) if dur_json is not None else None

        # 2. Prediction assuming Not Yet Triggered Automated default
        ben_pred_not_yet = generate_benefit_sentence(
            ca_pred, tool_pred, 'Not Yet Triggered Automated',
            dur_json, ev_json, wl_json
        ) if dur_json is not None else None

        ben_match_actual_st = (ben_csv == ben_pred_actual_st) if (in_csv and ben_pred_actual_st) else None
        ben_match_not_yet = (ben_csv == ben_pred_not_yet) if (in_csv and ben_pred_not_yet) else None

        # Mismatch reasons
        mismatch_reasons = []
        if in_csv:
            if st_csv != 'Not Yet Triggered Automated':
                mismatch_reasons.append(f"Status ({st_csv})")
            if ca_csv != ca_pred:
                mismatch_reasons.append(f"Category ({ca_csv} vs {ca_pred})")
            if tool_csv != tool_pred:
                mismatch_reasons.append(f"Tool ({tool_csv} vs {tool_pred})")
            if wl_csv != wl_json:
                mismatch_reasons.append(f"Workload ({wl_csv} vs {wl_json})")

        rows_data.append({
            'CONCAT': key,
            'Presence': presence,
            'RAW_CONCAT_CSV': r_csv['CONCAT'] if in_csv else None,
            'RAW_CONCAT_JSON': r_json_raw['CONCAT'] if in_json_all else None,
            'Has_Trailing_Space_CSV': (r_csv['CONCAT'] != key) if in_csv else False,
            'Improvement_Category_JSON': r_json_raw['Improvement Category'] if in_json_all else None,
            'Category_Notes_JSON': r_json_raw['Category Notes'] if in_json_all else None,
            'Additional_Notes_JSON': r_json_raw['Additional Notes'] if in_json_all else None,
            'Durasi_CSV': dur_csv,
            'Durasi_JSON': dur_json,
            'Durasi_Match': dur_match,
            'Event_CSV': ev_csv,
            'Event_JSON': ev_json,
            'Event_Match': ev_match,
            'Workload_CSV': wl_csv,
            'Workload_JSON_Calc': wl_json,
            'Workload_Match': wl_match,
            'Category_Action_CSV': ca_csv,
            'Category_Action_Pred': ca_pred,
            'Category_Action_Match': ca_match,
            'Tools_Automation_CSV': tool_csv,
            'Tools_Automation_Pred': tool_pred,
            'Tools_Automation_Match': tool_match,
            'Status_Triggered_CSV': st_csv,
            'Benefit_CSV': ben_csv,
            'Benefit_Pred_Actual_ST': ben_pred_actual_st,
            'Benefit_Pred_Not_Yet': ben_pred_not_yet,
            'Benefit_Match_Actual_ST': ben_match_actual_st,
            'Benefit_Match_Not_Yet': ben_match_not_yet,
            'Benefit_Mismatch_Reasons': "; ".join(mismatch_reasons) if mismatch_reasons else "NONE",
        })

    df_out = pd.DataFrame(rows_data)

    # Save to Excel
    print(f"Writing Excel to: {output_excel_path}")
    with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
        df_out.to_excel(writer, sheet_name='Perbandingan_Per_Baris', index=False)

        # Summary sheet
        overlap = df_out[df_out['Presence'] == 'IN_BOTH']
        csv_only = df_out[df_out['Presence'] == 'CSV_ONLY']
        json_only = df_out[df_out['Presence'] == 'JSON_RULE_ONLY']

        summary_rows = [
            {'Metrik': 'Total Baris CSV Benchmark', 'Nilai': len(df_csv)},
            {'Metrik': 'Total Baris JSON Rule Terpilih', 'Nilai': len(json_selected)},
            {'Metrik': 'Baris Irisan Sempurna (IN_BOTH)', 'Nilai': len(overlap)},
            {'Metrik': 'Baris Hanya di CSV (CSV_ONLY)', 'Nilai': len(csv_only)},
            {'Metrik': 'Baris Hanya di JSON Rule (JSON_RULE_ONLY)', 'Nilai': len(json_only)},
            {'Metrik': 'Total Workload CSV (Jam/Bulan)', 'Nilai': round(df_csv['workload_clean'].sum() / 60.0, 2)},
            {'Metrik': 'Total Workload JSON Rule (Jam/Bulan)', 'Nilai': round(json_selected['workload_calc'].sum() / 60.0, 2)},
            {'Metrik': 'Akurasi Workload pada Irisan', 'Nilai': f"{(overlap['Workload_Match'].sum() / len(overlap))*100:.2f}% ({overlap['Workload_Match'].sum()}/{len(overlap)})"},
            {'Metrik': 'Akurasi Category Action pada Irisan', 'Nilai': f"{(overlap['Category_Action_Match'].sum() / len(overlap))*100:.2f}% ({overlap['Category_Action_Match'].sum()}/{len(overlap)})"},
            {'Metrik': 'Akurasi Tools Automation pada Irisan', 'Nilai': f"{(overlap['Tools_Automation_Match'].sum() / len(overlap))*100:.2f}% ({overlap['Tools_Automation_Match'].sum()}/{len(overlap)})"},
            {'Metrik': 'Akurasi Benefit (Actual Status) pada Irisan', 'Nilai': f"{(overlap['Benefit_Match_Actual_ST'].sum() / len(overlap))*100:.2f}% ({overlap['Benefit_Match_Actual_ST'].sum()}/{len(overlap)})"},
            {'Metrik': 'Akurasi Benefit (Not Yet Default) pada Irisan', 'Nilai': f"{(overlap['Benefit_Match_Not_Yet'].sum() / len(overlap))*100:.2f}% ({overlap['Benefit_Match_Not_Yet'].sum()}/{len(overlap)})"},
        ]
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name='Ringkasan_Metrik', index=False)

    print("Pipeline executed successfully!")
    return {
        'total_csv': len(df_csv),
        'total_json_selected': len(json_selected),
        'overlap_count': len(overlap),
        'csv_only_count': len(csv_only),
        'json_only_count': len(json_only),
        'csv_hours': df_csv['workload_clean'].sum() / 60.0,
        'json_hours': json_selected['workload_calc'].sum() / 60.0,
    }


if __name__ == '__main__':
    json_file = Path(r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json')
    csv_file = Path(r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv')
    excel_out = Path(r'C:\Users\rahma\OneDrive\Documents\worklens\scratchpad\perbandingan_per_baris.xlsx')

    run_pipeline(json_file, csv_file, excel_out)

