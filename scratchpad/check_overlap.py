import json
import pandas as pd
import re

json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'
csv_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'

with open(json_path, 'r', encoding='utf-8') as f:
    raw_json = json.load(f)['value']

df_json = pd.DataFrame(raw_json)
df_csv = pd.read_csv(csv_path)

# Let's inspect CONCAT matching
# Notice trailing whitespace issue:
csv_concat_raw = set(df_csv['CONCAT'])
csv_concat_stripped = {c.strip(): c for c in df_csv['CONCAT']}
json_concat_raw = set(df_json['CONCAT'])
json_concat_stripped = {c.strip(): c for c in df_json['CONCAT']}

print(f"Unique CSV CONCAT: raw={len(csv_concat_raw)}, stripped={len(csv_concat_stripped)}")
print(f"Unique JSON CONCAT: raw={len(json_concat_raw)}, stripped={len(json_concat_stripped)}")

# How many CSV rows are in JSON?
exact_matches = csv_concat_raw.intersection(json_concat_raw)
stripped_matches = set(csv_concat_stripped.keys()).intersection(set(json_concat_stripped.keys()))

print(f"Exact CONCAT matches: {len(exact_matches)}")
print(f"Stripped CONCAT matches: {len(stripped_matches)}")

# Rows in CSV but not in JSON:
csv_only = set(csv_concat_stripped.keys()) - set(json_concat_stripped.keys())
print(f"CSV only (stripped): {len(csv_only)}")
if csv_only:
    print("Sample CSV only:", list(csv_only)[:5])

# Let's check the user's statement:
# '650 dari 658 baris CSV yang ada di JSON tertangkap, 23 baris ekstra di JSON, 17 baris hanya di CSV.'
# 667 total CSV rows = 658 present in JSON + 9 NOT present? Or 667 - 650 = 17?
# Let's check!
print(f"Total CSV: {len(df_csv)}")
print(f"Total CSV stripped: {len(csv_concat_stripped)}")
print(f"CSV keys in JSON: {len(stripped_matches)}")
print(f"CSV keys not in JSON: {len(df_csv) - len(stripped_matches)}")

