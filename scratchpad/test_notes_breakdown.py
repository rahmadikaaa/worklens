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

# Let's see the total workload of CSV
df_csv['workload_num'] = df_csv['Workload'].apply(clean_num)
csv_total_hours = df_csv['workload_num'].sum() / 60.0
print(f"CSV Total Workload (hours): {csv_total_hours:.2f} (expected ~623.8 or 624)")

# Now let's test the rule definition:
# The user prompt states:
# "Pemilihan baris: Improvement Category = 'Automation', Event Per Month ≥ 1, dan Additional Notes termasuk keluarga 'Already automate' (termasuk 'via ITOC', 'via DSC', 'Already AI', 'Health Check', 'No Action', 'GUI', 'Need further assessment', dll). Dengan rule ini: 650 dari 658 baris CSV yang ada di JSON tertangkap, 23 baris ekstra di JSON, 17 baris hanya di CSV."

# Let's inspect all unique Additional Notes in df_json where Improvement Category == 'Automation' and event_num >= 1
sub = df_json[(df_json['Improvement Category'] == 'Automation') & (df_json['event_num'] >= 1)].copy()

# Let's check for each note: how many in CSV, how many not in CSV, and workload sum
note_stats = []
for note, grp in sub.groupby(sub['Additional Notes'].str.strip()):
    in_csv = grp['concat_clean'].isin(csv_keys).sum()
    not_in_csv = len(grp) - in_csv
    hours = grp['workload_calc'].sum() / 60.0
    note_stats.append({
        'note': note,
        'total': len(grp),
        'in_csv': in_csv,
        'not_in_csv': not_in_csv,
        'hours': hours
    })

df_notes = pd.DataFrame(note_stats).sort_values(by='total', ascending=False)
print(df_notes.to_string())

