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
df_json['concat_clean'] = df_json['CONCAT'].str.strip()
df_csv['concat_clean'] = df_csv['CONCAT'].str.strip()

csv_keys = set(df_csv['concat_clean'])

# Let's inspect which Additional Notes appear in CSV vs JSON
in_csv_notes = set(df_json[df_json['concat_clean'].isin(csv_keys)]['Additional Notes'].unique())
print("Additional notes present in CSV:")
for n in sorted(in_csv_notes):
    print(f"  - '{n}'")

# Let's see if excluding alert/cron-related notes or defining a whitelist gives 673 rows
# In the prompt:
# "Additional Notes termasuk keluarga 'Already automate' (termasuk 'via ITOC', 'via DSC', 'Already AI', 'Health Check', 'No Action', 'GUI', 'Need further assessment', dll)"
# Notice that 'Alert already exist', 'Sudah ada alert', 'Create alert', 'Cron already exist', '0', '' are excluded.

# Let's test what filter gives exactly 673 rows:
# Let's check candidates among sub:
sub = df_json[(df_json['Improvement Category'] == 'Automation') & (df_json['event_num'] >= 1)]

# Let's see what happens if we exclude:
excluded_notes = {'Alert already exist', 'Sudah ada alert', 'Create alert', 'Cron already exist', '0', '', ' '}
selected = sub[~sub['Additional Notes'].str.strip().isin(excluded_notes)]
print(f"Selected without alert/cron/0/empty: {len(selected)}")
print(f"Matches in CSV: {len(set(selected['concat_clean']).intersection(csv_keys))}")
print(f"Extra in JSON: {len(selected) - len(set(selected['concat_clean']).intersection(csv_keys))}")
print(f"CSV not captured: {len(csv_keys) - len(set(selected['concat_clean']).intersection(csv_keys))}")

# Let's check which notes are in selected:
print("\nNotes in selected:")
print(selected['Additional Notes'].value_counts())

