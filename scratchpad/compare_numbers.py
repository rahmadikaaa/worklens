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

df_json['durasi_num'] = df_json['Durasi (Menit)'].apply(clean_num)
df_json['event_num'] = df_json['Event Per Month'].apply(clean_num)
df_json['workload_raw'] = df_json['Workload'].apply(clean_num)
df_json['workload_calc'] = df_json['durasi_num'] * df_json['event_num']
df_json['concat_clean'] = df_json['CONCAT'].str.strip()

df_csv['durasi_num'] = df_csv['Durasi (Menit)'].apply(clean_num)
df_csv['event_num'] = df_csv['Event Per Month'].apply(clean_num)
df_csv['workload_num'] = df_csv['Workload'].apply(clean_num)
df_csv['concat_clean'] = df_csv['CONCAT'].str.strip()

# Join on concat_clean
merged = pd.merge(df_csv, df_json, on='concat_clean', suffixes=('_csv', '_json'))
print(f"Total merged rows (out of 667 CSV): {len(merged)}")

# Compare Durasi
dur_diff = merged[merged['durasi_num_csv'] != merged['durasi_num_json']]
print(f"\nDurasi differences: {len(dur_diff)}")
for idx, r in dur_diff.iterrows():
    print(f"  {r['concat_clean']}: CSV={r['durasi_num_csv']} vs JSON={r['durasi_num_json']}")

# Compare Event
evt_diff = merged[merged['event_num_csv'] != merged['event_num_json']]
print(f"\nEvent differences: {len(evt_diff)}")
for idx, r in evt_diff.iterrows():
    print(f"  {r['concat_clean']}: CSV={r['event_num_csv']} vs JSON={r['event_num_json']}")

# Compare Workload (CSV Workload vs JSON Workload raw, and vs JSON Workload calc)
wl_diff_raw = merged[merged['workload_num'] != merged['workload_raw']]
print(f"\nWorkload differences (CSV vs JSON raw): {len(wl_diff_raw)}")
for idx, r in wl_diff_raw.iterrows():
    print(f"  {r['concat_clean']}: CSV={r['workload_num']} vs JSON_raw={r['workload_raw']} vs JSON_calc={r['workload_calc']}")

# Also let's check Workload = Durasi * Event in CSV
csv_formula_diff = df_csv[df_csv['workload_num'] != (df_csv['durasi_num'] * df_csv['event_num'])]
print(f"\nCSV internal formula (Workload != Durasi * Event): {len(csv_formula_diff)}")

