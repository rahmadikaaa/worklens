import json
import pandas as pd
import re

json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'
csv_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'

with open(json_path, 'r', encoding='utf-8') as f:
    raw_json = json.load(f)['value']

df_json = pd.DataFrame(raw_json)
df_csv = pd.read_csv(csv_path)

def clean_num(val):
    if val is None or pd.isna(val): return 0.0
    s = str(val).strip().replace(',', '.')
    m = re.search(r'^-?\d+(?:\.\d+)?', s)
    return float(m.group(0)) if m else 0.0

df_json['event_num'] = df_json['Event Per Month'].apply(clean_num)
df_json['durasi_num'] = df_json['Durasi (Menit)'].apply(clean_num)
df_json['workload_calc'] = df_json['durasi_num'] * df_json['event_num']
df_json['concat_raw'] = df_json['CONCAT']
csv_exact = set(df_csv['CONCAT'])

rule_notes = [
    'Already automate',
    'via ITOC',
    'via DSC',
    'Already AI',
    'No Action',
    'Already healthcheck',
    'GUI',
    'Need further assessment',
    'Already CICD',
    'Already empower',
    'Automate',
    'Health Check',
    'Already healtchechk',
    'Need Further Assesment',
    'Already Automate'
]

sub = df_json[(df_json['Improvement Category'] == 'Automation') & (df_json['event_num'] >= 1)].copy()
selected = sub[sub['Additional Notes'].isin(rule_notes)].copy()

matches = selected[selected['concat_raw'].isin(csv_exact)]
extra = selected[~selected['concat_raw'].isin(csv_exact)]

print(f"Total Selected: {len(selected)}")
print(f"Matches in CSV (exact): {len(matches)}")
print(f"Extra in JSON: {len(extra)}")
print(f"Total Hours in Selected: {selected['workload_calc'].sum() / 60.0:.2f} hours")
print(f"Total Hours in Matches: {matches['workload_calc'].sum() / 60.0:.2f} hours")
print(f"Total Hours in Extra: {extra['workload_calc'].sum() / 60.0:.2f} hours")

df_csv['workload_num'] = df_csv['Workload'].apply(clean_num)
print(f"Total Hours in CSV: {df_csv['workload_num'].sum() / 60.0:.2f} hours")

