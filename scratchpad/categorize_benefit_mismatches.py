import pandas as pd
import json
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
    import re
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

# Now, suppose we predict Benefit assuming 'Not Yet Triggered Automated'
# Let's inspect each row that doesn't match:
mismatches_causes = []
for idx, r in merged.iterrows():
    actual_b = r['Benefit'].strip()
    pred_b = generate_canonical_benefit(
        r['pred_ca'],
        r['pred_tool'],
        'Not Yet Triggered Automated',
        r['durasi_num_json'],
        r['event_num_json'],
        r['workload_calc_num']
    )
    if actual_b != pred_b:
        causes = []
        # Check Status Triggered
        if r['Status Triggered'] != 'Not Yet Triggered Automated':
            causes.append('status')
        # Check Tool
        if r['pred_tool'] != r['Tools Automation_csv']:
            causes.append('tool')
        # Check Category
        if r['pred_ca'] != r['Category Action_csv']:
            causes.append('kategori')
        # Check Angka
        if (r['durasi_num_json'] != r['durasi_num_csv']) or (r['event_num_json'] != r['event_num_csv']) or (r['workload_calc_num'] != r['workload_num']):
            causes.append('angka')
            
        mismatches_causes.append({
            'concat': r['concat_clean'],
            'causes': causes,
            'primary_cause': causes[0] if causes else 'other',
            'status_actual': r['Status Triggered'],
            'tool_pred': r['pred_tool'],
            'tool_actual': r['Tools Automation_csv'],
            'ca_pred': r['pred_ca'],
            'ca_actual': r['Category Action_csv'],
        })

df_mm = pd.DataFrame(mismatches_causes)
print(f"Total Benefit mismatches (when assuming Not Yet): {len(df_mm)}")
print("\nCause frequencies (can have multiple causes per row):")
from collections import Counter
all_causes = [c for row_c in df_mm['causes'] for c in row_c]
print(Counter(all_causes))

print("\nPrimary cause distribution:")
print(df_mm['primary_cause'].value_counts())

