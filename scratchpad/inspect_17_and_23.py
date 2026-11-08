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
df_json['concat_clean'] = df_json['CONCAT'].str.strip()

df_csv['concat_raw'] = df_csv['CONCAT']
df_csv['concat_clean'] = df_csv['CONCAT'].str.strip()
df_csv['workload_num'] = df_csv['Workload'].apply(clean_num)

rule_notes = [
    'Already automate', 'via ITOC', 'via DSC', 'Already AI', 'No Action',
    'Already healthcheck', 'GUI', 'Need further assessment', 'Already CICD',
    'Already empower', 'Automate', 'Health Check', 'Already healtchechk',
    'Need Further Assesment', 'Already Automate'
]

sub = df_json[(df_json['Improvement Category'] == 'Automation') & (df_json['event_num'] >= 1)].copy()
selected = sub[sub['Additional Notes'].isin(rule_notes)].copy()

selected_exact = set(selected['concat_raw'])
selected_clean = set(selected['concat_clean'])

# 17 rows in CSV not matched exactly by rule:
csv_not_matched_exact = df_csv[~df_csv['concat_raw'].isin(selected_exact)].copy()
print(f"Count of CSV rows not matched exactly by rule: {len(csv_not_matched_exact)}")

# Let's inspect each of these 17 rows:
print("\n--- The 17 CSV rows ---")
for idx, r in csv_not_matched_exact.iterrows():
    c_raw = r['concat_raw']
    c_clean = r['concat_clean']
    # Check if present in df_json (clean)
    j_match = df_json[df_json['concat_clean'] == c_clean]
    if len(j_match) > 0:
        jr = j_match.iloc[0]
        has_trailing_space = (c_raw != c_clean)
        in_selected_clean = c_clean in selected_clean
        print(f"CSV CONCAT: {c_raw!r}")
        print(f"  Trailing space in CSV: {has_trailing_space}")
        print(f"  In selected (if stripped): {in_selected_clean}")
        print(f"  JSON values -> Improvement Cat: {jr['Improvement Category']!r}, Category Notes: {jr['Category Notes']!r}, Add Notes: {jr['Additional Notes']!r}, Durasi: {jr['Durasi (Menit)']}, Event: {jr['Event Per Month']}, Workload: {jr['Workload']}")
    else:
        print(f"CSV CONCAT: {c_raw!r} -> NOT FOUND IN JSON AT ALL!")

print("\n--- The 23 Extra JSON rows ---")
json_extra = selected[~selected['concat_raw'].isin(set(df_csv['concat_raw']))].copy()
print(f"Count of JSON extra rows: {len(json_extra)}")
for idx, r in json_extra.iterrows():
    c_clean = r['concat_clean']
    in_csv_clean = c_clean in set(df_csv['concat_clean'])
    print(f"JSON CONCAT: {r['CONCAT']!r} | in CSV if stripped: {in_csv_clean} | Hours: {r['workload_calc']/60:.2f} | Notes: {r['Additional Notes']!r} | Durasi: {r['Durasi (Menit)']} | Event: {r['Event Per Month']}")

