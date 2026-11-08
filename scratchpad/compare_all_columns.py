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
df_json['workload_raw_num'] = df_json['Workload'].apply(clean_num)
df_json['workload_calc_num'] = df_json['durasi_num'] * df_json['event_num']
df_json['concat_clean'] = df_json['CONCAT'].str.strip()

df_csv['durasi_num'] = df_csv['Durasi (Menit)'].apply(clean_num)
df_csv['event_num'] = df_csv['Event Per Month'].apply(clean_num)
df_csv['workload_num'] = df_csv['Workload'].apply(clean_num)
df_csv['concat_clean'] = df_csv['CONCAT'].str.strip()

merged = pd.merge(df_csv, df_json, on='concat_clean', suffixes=('_csv', '_json'))

# Check all numerical differences
for col in ['durasi_num', 'event_num', 'workload_num']:
    if col == 'workload_num':
        diff1 = merged[merged['workload_num'] != merged['workload_raw_num']]
        diff2 = merged[merged['workload_num'] != merged['workload_calc_num']]
        print(f"workload_num vs raw diffs: {len(diff1)}")
        for idx, r in diff1.iterrows():
            print(f"  {r['concat_clean']}: CSV={r['workload_num']} vs JSON_raw={r['workload_raw_num']}")
        print(f"workload_num vs calc diffs: {len(diff2)}")
        for idx, r in diff2.iterrows():
            print(f"  {r['concat_clean']}: CSV={r['workload_num']} vs JSON_calc={r['workload_calc_num']}")
    else:
        diff = merged[merged[f'{col}_csv'] != merged[f'{col}_json']]
        print(f"{col} diffs: {len(diff)}")
        for idx, r in diff.iterrows():
            print(f"  {r['concat_clean']}: CSV={r[f'{col}_csv']} vs JSON={r[f'{col}_json']}")

# What about the 23 extra rows? Do any of them have differences?
# Or what about other files in backend/uploads, e.g. 261105_1704?

