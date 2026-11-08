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

sub = df_json[(df_json['Improvement Category'] == 'Automation') & (df_json['event_num'] >= 1)].copy()

# We know:
# C2P - C2P MASSTOOL RECORD NOT FOUND has note 'Already Automate' (hours=31.0)
# Telkomsel Portal - Tselid Clicker Report has note 'Already automate' (hours=30.0)
# And total hours is 708.8!
# Let's find which notes were included in the filter to give exactly 673 rows:
# Let's see:
# Let's list all notes and see their count in sub, exact match with CSV, and extra:
notes_info = {}
for note, grp in sub.groupby(sub['Additional Notes']):
    match_cnt = grp['concat_raw'].isin(csv_exact).sum()
    tot_cnt = len(grp)
    hrs = grp['workload_calc'].sum() / 60.0
    notes_info[note] = {'total': tot_cnt, 'match': match_cnt, 'extra': tot_cnt - match_cnt, 'hours': hrs}

# Let's print notes_info sorted by total
for k, v in sorted(notes_info.items(), key=lambda x: x[1]['total'], reverse=True):
    print(f"{k!r}: {v}")

