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
sub = df_json[(df_json['Improvement Category'] == 'Automation') & (df_json['event_num'] >= 1)].copy()

# Note that in Analisis_Peluang_Otomasi_L1.md:
# "Additional Notes termasuk keluarga 'Already automate' (termasuk 'via ITOC', 'via DSC', 'Already AI', 'Health Check', 'No Action', 'GUI', 'Need further assessment', dll)."
# Let's see: which notes when combined give:
# in_csv == 650, total == 673 (not_in_csv == 23), hours == ~708.8

# Let's inspect which notes have in_csv > 0:
# 'Already automate': 601 in_csv, 4 not_in_csv (total 605)
# 'via ITOC': 27 in_csv, 1 not_in_csv (total 28)
# 'via DSC': 7 in_csv, 0 not_in_csv (total 7)
# 'Already AI': 6 in_csv, 1 not_in_csv (total 7)
# 'No Action': 3 in_csv, 3 not_in_csv (total 6)
# 'Already healthcheck': 3 in_csv, 0 not_in_csv (total 3)
# 'Health Check': 2 in_csv, 0 not_in_csv (total 2)
# 'Already CICD': 2 in_csv, 0 not_in_csv (total 2)
# 'Automate': 2 in_csv, 0 not_in_csv (total 2)
# 'Need further assessment': 2 in_csv, 1 not_in_csv (total 3)
# 'GUI': 1 in_csv, 2 not_in_csv (total 3)
# 'Already empower': 1 in_csv, 1 not_in_csv (total 2)
# 'Already healtchechk': 1 in_csv, 0 not_in_csv (total 1)
# 'Need Further Assesment': 1 in_csv, 0 not_in_csv (total 1)

# Sum of all notes with in_csv > 0:
# in_csv = 601 + 27 + 7 + 6 + 3 + 3 + 2 + 2 + 2 + 2 + 1 + 1 + 1 + 1 = 659 in_csv!
# Wait! 659 > 650! Why did the author say 650?
# Let's check:
# 1) Did the author NOT strip CONCAT? (exact matches were 658, not 667!)
# If exact match was used without strip:
# Let's calculate matches with exact CONCAT:
csv_exact = set(df_csv['CONCAT'])
for note, grp in sub.groupby(sub['Additional Notes'].str.strip()):
    exact_in_csv = grp['CONCAT'].isin(csv_exact).sum()
    clean_in_csv = grp['concat_clean'].isin(csv_keys).sum()
    if exact_in_csv != clean_in_csv:
        print(f"Difference for '{note}': exact={exact_in_csv}, clean={clean_in_csv}")

# Also, what if Category Notes or Phase was used?
# Let's check!

