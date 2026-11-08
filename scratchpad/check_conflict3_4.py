import csv

csv_eod_path = r'C:\Users\rahma\Downloads\AGIT L1 EOD Daily Report (4).csv'

lines = open(csv_eod_path, 'r', encoding='utf-8', errors='ignore').readlines()
header = [h.strip() for h in lines[2].split(';')]
eod_rows = list(csv.DictReader(lines[3:], fieldnames=header, delimiter=';'))

print(f"Total EOD rows: {len(eod_rows)}")

# Distribution of APP PRIORITY in EOD
prio_counts = {}
for r in eod_rows:
    p = str(r.get('APP PRIORITY') or '').strip() or 'No Priority'
    prio_counts[p] = prio_counts.get(p, 0) + 1

print("\nAPP PRIORITY in EOD CSV (total 667):")
for k, v in sorted(prio_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Let's inspect 'Current Status (develpment/ testing / Ready to Deploy)'
cs_counts = {}
for r in eod_rows:
    cs = str(r.get('Current Status (develpment/ testing / Ready to Deploy)') or '').strip()
    cs_counts[cs] = cs_counts.get(cs, 0) + 1

print("\nCurrent Status in EOD CSV:")
for k, v in sorted(cs_counts.items(), key=lambda x: -x[1]):
    print(f"  {k!r}: {v}")

# Cross tab of APP PRIORITY vs Current Status
cross_tab = {}
for r in eod_rows:
    p = str(r.get('APP PRIORITY') or '').strip() or 'No Priority'
    cs = str(r.get('Current Status (develpment/ testing / Ready to Deploy)') or '').strip()
    key = (p, cs)
    cross_tab[key] = cross_tab.get(key, 0) + 1

print("\nCross-tab of APP PRIORITY vs Current Status in EOD:")
for (p, cs), cnt in sorted(cross_tab.items(), key=lambda x: (x[0][0], -x[1])):
    print(f"  {p:20} | {cs:20} : {cnt}")

