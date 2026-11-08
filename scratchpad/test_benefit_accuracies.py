import pandas as pd
import json
import re
import sys
sys.path.append(r'C:\Users\rahma\OneDrive\Documents\worklens')
from backend.app.services.discovery_service import generate_canonical_benefit

csv_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'
json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'

df_csv = pd.read_csv(csv_path)
with open(json_path, 'r', encoding='utf-8') as f:
    raw_json = json.load(f)['value']
df_json = pd.DataFrame(raw_json)

def clean_num(val):
    if val is None or pd.isna(val): return 0.0
    s = str(val).strip().replace(',', '.')
    m = re.search(r'^-?\d+(?:\.\d+)?', s)
    return float(m.group(0)) if m else 0.0

df_json['durasi_num'] = df_json['Durasi (Menit)'].apply(clean_num)
df_json['event_num'] = df_json['Event Per Month'].apply(clean_num)
df_json['workload_calc_num'] = df_json['durasi_num'] * df_json['event_num']
df_json['concat_clean'] = df_json['CONCAT'].str.strip()

df_csv['durasi_num'] = df_csv['Durasi (Menit)'].apply(clean_num)
df_csv['event_num'] = df_csv['Event Per Month'].apply(clean_num)
df_csv['workload_num'] = df_csv['Workload'].apply(clean_num)
df_csv['concat_clean'] = df_csv['CONCAT'].str.strip()

merged = pd.merge(df_csv, df_json, on='concat_clean', suffixes=('_csv', '_json'))

# Let's predict CA and Tool
def predict_ca(row):
    t_act = str(row.get('TYPE ACTIVITY', '')).strip()
    act = str(row.get('ACTIVITY NAME', '')).strip().lower()
    if t_act == 'Housekeeping' or any(k in act for k in ['housekeeping', 'clear log', 'delete log', 'clear event', 'clean log', 'cleanup']):
        return 'Auto Housekeeping'
    if t_act in ['Service Request', 'Complaint Handling', 'Change Management']:
        return 'Self Service Request'
    if any(k in act for k in ['restart bot', 'running manual bot', 'restart service cypress', 'restart admin api']):
        return 'Auto Restart'
    if any(k in act for k in ['check process', 'check service', 'check memory', 'health check', 'healthcheck', 'check disk', 'storage usage', 'cpu usage']):
        return 'Health Check'
    if t_act in ['Daily Activity', 'Monitoring and Alerting'] or any(k in act for k in ['monitoring', 'grafana', 'traffic', 'success rate', 'error count', 'trend error']):
        return 'Auto Monitoring'
    if t_act == 'Incident Handling' or any(k in act for k in ['restart', 'start stop', 'reboot', 'kill', 'recycle', 'stop and start']):
        return 'Smart Healing'
    return 'Smart Healing'

def predict_tool(row):
    t = str(row.get('Tools Automation_json', '')).strip()
    act = str(row.get('ACTIVITY NAME', '')).lower()
    if t.lower() == 'shell script':
        if 'grafana' in act: return 'Grafana'
        return 'Shell Script'
    if t == 'Not Automate':
        if 'grafana' in act: return 'Grafana'
        return 'AION'
    return t

merged['pred_ca'] = merged.apply(predict_ca, axis=1)
merged['pred_tool'] = merged.apply(predict_tool, axis=1)

# Case 1: Assuming all 'Not Yet Triggered Automated'
def gen_ben_not_yet(row):
    return generate_canonical_benefit(
        row['pred_ca'],
        row['pred_tool'],
        'Not Yet Triggered Automated',
        row['durasi_num_json'],
        row['event_num_json'],
        row['workload_calc_num']
    )

merged['pred_ben_not_yet'] = merged.apply(gen_ben_not_yet, axis=1)
match_all_not_yet = (merged['pred_ben_not_yet'] == merged['Benefit'].str.strip()).mean()

# On rows where CSV Status Triggered is 'Not Yet Triggered Automated':
not_yet_subset = merged[merged['Status Triggered'] == 'Not Yet Triggered Automated']
match_on_not_yet = (not_yet_subset['pred_ben_not_yet'] == not_yet_subset['Benefit'].str.strip()).mean()

print(f"Benefit match across ALL rows (assuming Not Yet): {match_all_not_yet*100:.2f}% ({sum(merged['pred_ben_not_yet'] == merged['Benefit'].str.strip())}/{len(merged)})")
print(f"Benefit match on CSV Not Yet rows: {match_on_not_yet*100:.2f}% ({sum(not_yet_subset['pred_ben_not_yet'] == not_yet_subset['Benefit'].str.strip())}/{len(not_yet_subset)})")

# Case 2: Using ground truth Status Triggered from CSV:
def gen_ben_actual_st(row):
    return generate_canonical_benefit(
        row['pred_ca'],
        row['pred_tool'],
        row['Status Triggered'],
        row['durasi_num_json'],
        row['event_num_json'],
        row['workload_calc_num']
    )

merged['pred_ben_actual_st'] = merged.apply(gen_ben_actual_st, axis=1)
match_actual_st = (merged['pred_ben_actual_st'] == merged['Benefit'].str.strip()).mean()
print(f"Benefit match with actual Status Triggered (predicted CA & Tool): {match_actual_st*100:.2f}% ({sum(merged['pred_ben_actual_st'] == merged['Benefit'].str.strip())}/{len(merged)})")

