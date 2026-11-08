import csv

csv_benefit_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'
csv_eod_path = r'C:\Users\rahma\Downloads\AGIT L1 EOD Daily Report (4).csv'

benefit_rows = []
with open(csv_benefit_path, 'r', encoding='utf-8', errors='ignore') as f:
    for r in csv.DictReader(f):
        benefit_rows.append(r)

eod_rows = []
with open(csv_eod_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
header = [h.strip() for h in lines[2].split(';')]
for r in csv.DictReader(lines[3:], fieldnames=header, delimiter=';'):
    if any(r.values()):
        eod_rows.append(r)

print(f"Benefit rows count: {len(benefit_rows)}")
print(f"EOD rows count: {len(eod_rows)}")

# Count Status Triggered in Benefit
benefit_st_counts = {}
for r in benefit_rows:
    st = r.get('Status Triggered', '').strip()
    benefit_st_counts[st] = benefit_st_counts.get(st, 0) + 1
print("\nBenefit CSV Status Triggered counts:")
for k, v in benefit_st_counts.items():
    print(f"  {k}: {v}")

# Count Status Triggered in EOD
eod_st_counts = {}
for r in eod_rows:
    st = r.get('Status Triggered', '').strip()
    eod_st_counts[st] = eod_st_counts.get(st, 0) + 1
print("\nEOD CSV Status Triggered counts:")
for k, v in eod_st_counts.items():
    print(f"  {k}: {v}")

# Map both by CONCAT
benefit_by_c = {r['CONCAT'].strip(): r for r in benefit_rows}
eod_by_c = {r['CONCAT'].strip(): r for r in eod_rows}

diffs = []
for c, br in benefit_by_c.items():
    er = eod_by_c.get(c)
    if not er:
        print(f"Missing in EOD: {c}")
        continue
    bst = br.get('Status Triggered', '').strip()
    est = er.get('Status Triggered', '').strip()
    if bst != est:
        diffs.append((c, bst, est, br, er))

print(f"\nNumber of differing rows: {len(diffs)}")
for c, bst, est, br, er in diffs:
    print(f"CONCAT: {c}")
    print(f"  Benefit CSV : '{bst}'")
    print(f"  EOD CSV     : '{est}'")
    print(f"  EOD notes   : '{er.get('Notes Status Triggered', '')}'")
    print(f"  EOD AO Tertrigger: '{er.get('AO Tertrigger', '')}', Workload AO Tertrigger: '{er.get('Workload AO Tertrigger', '')}'")
    print(f"  EOD WL Manual After: '{er.get('Workload Manual After', '')}', WL Manual Triggered: '{er.get('Workload Manual Triggered', '')}'")

