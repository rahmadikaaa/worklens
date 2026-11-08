import json
import csv
import io
import sys

json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'
csv_benefit_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'
csv_eod_path = r'C:\Users\rahma\Downloads\AGIT L1 EOD Daily Report (4).csv'

print("=== 1. LOADING DATASETS ===")
with open(json_path, 'r', encoding='utf-8') as f:
    json_raw = json.load(f)
json_rows = json_raw['value']
print(f"JSON rows count: {len(json_rows)}")

# Read Benefit CSV
benefit_rows = []
with open(csv_benefit_path, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f)
    for r in reader:
        benefit_rows.append(r)
print(f"Benefit CSV rows count: {len(benefit_rows)}")

# Read EOD CSV (delimiter ';', header on line 3)
eod_rows = []
with open(csv_eod_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
eod_header_line = lines[2]
eod_data_lines = lines[3:]
reader = csv.DictReader(eod_data_lines, fieldnames=[h.strip() for h in eod_header_line.split(';')], delimiter=';')
for r in reader:
    if any(r.values()):
        eod_rows.append(r)
print(f"EOD CSV rows count: {len(eod_rows)}")

print("\n=== 2. RE-PROFILE REFERENCE NUMBERS FROM JSON ===")
total_records = len(json_rows)

def parse_num(v):
    if v is None:
        return None
    s = str(v).strip().replace(',', '.')
    if not s or s.lower() == 'null':
        return None
    try:
        return float(s)
    except:
        return None

workloads = []
workload_afters = []
positive_wl = 0
zero_wl = 0
invalid_wl = 0

done_count = 0
blank_assessment = 0

app_priority_counts = {}
tools_counts = {}
cat_notes_counts = {}
new_imp_fixed_counts = {}

for r in json_rows:
    wl = parse_num(r.get('Workload'))
    wla = parse_num(r.get('Workload after'))
    
    if wl is not None:
        workloads.append(wl)
        if wl > 0:
            positive_wl += 1
        elif wl == 0:
            zero_wl += 1
        else:
            invalid_wl += 1
    else:
        invalid_wl += 1
        
    if wla is not None:
        workload_afters.append(wla)
        
    st = str(r.get('Status') or '').strip()
    if st.lower() == 'done':
        done_count += 1
    elif not st:
        blank_assessment += 1
        
    prio = str(r.get('APP PRIORITY') or '').strip() or '#N/A'
    app_priority_counts[prio] = app_priority_counts.get(prio, 0) + 1
    
    tool = str(r.get('Tools Automation') or '').strip()
    if not tool:
        tool = 'Blank'
    tools_counts[tool] = tools_counts.get(tool, 0) + 1
    
    cn = str(r.get('Category Notes') or '').strip()
    cat_notes_counts[cn] = cat_notes_counts.get(cn, 0) + 1
    
    nif = str(r.get('New Improvement Category Fixed') or '').strip()
    new_imp_fixed_counts[nif] = new_imp_fixed_counts.get(nif, 0) + 1

total_wl_hours = sum(workloads) / 60.0
total_wla_hours = sum(workload_afters) / 60.0

print(f"Total records: {total_records}")
print(f"Total Workload (sum/60): {total_wl_hours:.1f} jam/bulan")
print(f"Total Workload after (sum/60): {total_wla_hours:.1f} jam/bulan")
print(f"Positive WL: {positive_wl}")
print(f"Zero WL: {zero_wl}")
print(f"Invalid / Missing WL: {invalid_wl}")
print(f"Assessment Done: {done_count}, Blank: {blank_assessment}")

print("\nAPP PRIORITY counts:")
for k, v in sorted(app_priority_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print("\nTools Automation counts (Top 10):")
for k, v in sorted(tools_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {k}: {v}")
shell_combined = tools_counts.get('Shell script', 0) + tools_counts.get('Shell Script', 0)
print(f"  Shell Script combined: {shell_combined} (Shell script: {tools_counts.get('Shell script', 0)}, Shell Script: {tools_counts.get('Shell Script', 0)})")

print("\nCategory Notes (Selected):")
print(f"  As Is: {cat_notes_counts.get('As Is', 0)}")
print(f"  Already Automated: {cat_notes_counts.get('Already Automated', 0)}")

print("\nNew Improvement Category Fixed (Selected):")
print(f"  As Is: {new_imp_fixed_counts.get('As Is', 0)}")

