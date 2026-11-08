import json
import pandas as pd
import re

p_old = r'C:\Users\rahma\OneDrive\Documents\worklens\backend\uploads\breakdown_activity_261105_1704_1.json'
csv_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'

with open(p_old, 'r', encoding='utf-8') as f:
    raw_old = json.load(f)['value']

df_old = pd.DataFrame(raw_old)
df_csv = pd.read_csv(csv_path)

def clean_num(val):
    if val is None or pd.isna(val): return 0.0
    s = str(val).strip().replace(',', '.')
    m = re.search(r'^-?\d+(?:\.\d+)?', s)
    return float(m.group(0)) if m else 0.0

df_old['durasi_num'] = df_old['Durasi (Menit)'].apply(clean_num)
df_old['event_num'] = df_old['Event Per Month'].apply(clean_num)
df_old['workload_raw_num'] = df_old['Workload'].apply(clean_num)
df_old['workload_calc_num'] = df_old['durasi_num'] * df_old['event_num']
df_old['concat_clean'] = df_old['CONCAT'].str.strip()

df_csv['durasi_num'] = df_csv['Durasi (Menit)'].apply(clean_num)
df_csv['event_num'] = df_csv['Event Per Month'].apply(clean_num)
df_csv['workload_num'] = df_csv['Workload'].apply(clean_num)
df_csv['concat_clean'] = df_csv['CONCAT'].str.strip()

merged = pd.merge(df_csv, df_old, on='concat_clean', suffixes=('_csv', '_old'))
diff = merged[merged['workload_num'] != merged['workload_raw_num']]
print("Differences in 261105_1704 vs CSV:")
for idx, r in diff.iterrows():
    print(r['concat_clean'], r['workload_num'], r['workload_raw_num'])

