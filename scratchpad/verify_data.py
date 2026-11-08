import json
import re
import pandas as pd
import numpy as np

json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'
csv_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'

with open(json_path, 'r', encoding='utf-8') as f:
    raw_json = json.load(f)['value']

df_json = pd.DataFrame(raw_json)
df_csv = pd.read_csv(csv_path)

print(f"Total JSON records: {len(df_json)}")
print(f"Total CSV records: {len(df_csv)}")

# 1. Number cleaning function
def clean_number(val):
    if val is None or pd.isna(val):
        return None
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ('n/a', 'nan', 'null', '-', '#value!', '#ref!', '#n/a'):
        return None
    # Indonesian comma to dot
    # Check if string has comma as decimal separator
    val_clean = val_str.replace(' ', '').replace(',', '.')
    # Extract number if it contains words like 'menit' e.g. '30 menit' -> 30
    match = re.search(r'^-?\d+(?:\.\d+)?', val_clean)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None

def parse_exact_float(val):
    if val is None or pd.isna(val):
        return None, "empty"
    val_str = str(val).strip()
    if not val_str:
        return None, "empty"
    # replace comma with dot
    v_norm = val_str.replace(',', '.')
    try:
        return float(v_norm), "valid"
    except ValueError:
        # text anomaly
        return None, "text_anomaly"

# Let's count duration and event text anomalies
dur_valid, dur_empty, dur_anomaly = 0, 0, 0
for v in df_json['Durasi (Menit)']:
    num, status = parse_exact_float(v)
    if status == 'valid': dur_valid += 1
    elif status == 'empty': dur_empty += 1
    else: dur_anomaly += 1

evt_valid, evt_empty, evt_anomaly = 0, 0, 0
for v in df_json['Event Per Month']:
    num, status = parse_exact_float(v)
    if status == 'valid': evt_valid += 1
    elif status == 'empty': evt_empty += 1
    else: evt_anomaly += 1

wl_empty = sum(df_json['Workload'].str.strip() == '')

print(f"Durasi: valid={dur_valid}, empty={dur_empty}, anomaly={dur_anomaly}")
print(f"Event: valid={evt_valid}, empty={evt_empty}, anomaly={evt_anomaly}")
print(f"Workload empty strings: {wl_empty}")

# Check Workload = Durasi * Event on raw records
formula_matches = 0
formula_total = 0
formula_mismatches = []

for idx, row in df_json.iterrows():
    d_num, d_st = parse_exact_float(row['Durasi (Menit)'])
    e_num, e_st = parse_exact_float(row['Event Per Month'])
    w_num, w_st = parse_exact_float(row['Workload'])
    if d_st == 'valid' and e_st == 'valid' and w_st == 'valid':
        formula_total += 1
        expected = d_num * e_num
        if abs(expected - w_num) < 1e-4:
            formula_matches += 1
        else:
            formula_mismatches.append((row['CONCAT'], d_num, e_num, w_num, expected))

print(f"Formula Workload = Durasi * Event matches: {formula_matches}/{formula_total} ({formula_matches/formula_total*100:.2f}%)")
if formula_mismatches:
    print(f"Mismatches: {len(formula_mismatches)}, e.g.: {formula_mismatches[:3]}")

