import json, csv

json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'
csv_eod_path = r'C:\Users\rahma\Downloads\AGIT L1 EOD Daily Report (4).csv'

with open(json_path, 'r', encoding='utf-8') as f:
    json_rows = json.load(f)['value']

eod_rows = []
with open(csv_eod_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
header = [h.strip() for h in lines[2].split(';')]
for r in csv.DictReader(lines[3:], fieldnames=header, delimiter=';'):
    if any(r.values()):
        eod_rows.append(r)

print("=== DEPARTMENTS & DIVISIONS IN JSON (ALL 3,460 ROWS) ===")
json_depts = {}
json_divs = {}
for r in json_rows:
    d = str(r.get('DEPT') or '').strip()
    v = str(r.get('DIV') or '').strip()
    json_depts[d] = json_depts.get(d, 0) + 1
    json_divs[v] = json_divs.get(v, 0) + 1

print("JSON Departments:")
for k, count in sorted(json_depts.items(), key=lambda x: -x[1]):
    print(f"  {k!r}: {count}")

print("\nJSON Divisions:")
for k, count in sorted(json_divs.items(), key=lambda x: -x[1]):
    print(f"  {k!r}: {count}")

print("\n=== DEPARTMENTS & DIVISIONS IN EOD (667 ROWS) ===")
eod_depts = {}
eod_divs = {}
for r in eod_rows:
    d = str(r.get('DEPT') or '').strip()
    v = str(r.get('DIV') or '').strip()
    eod_depts[d] = eod_depts.get(d, 0) + 1
    eod_divs[v] = eod_divs.get(v, 0) + 1

print("EOD Departments:")
for k, count in sorted(eod_depts.items(), key=lambda x: -x[1]):
    print(f"  {k!r}: {count}")

print("\nEOD Divisions:")
for k, count in sorted(eod_divs.items(), key=lambda x: -x[1]):
    print(f"  {k!r}: {count}")

print("\n=== ROW-BY-ROW COMPARISON FOR THE 667 INTERSECTING ROWS ===")
json_by_c = {str(r.get('CONCAT') or '').strip(): r for r in json_rows}
dept_pairs = {}
div_pairs = {}

for er in eod_rows:
    c = er['CONCAT'].strip()
    jr = json_by_c.get(c)
    if jr:
        jd = str(jr.get('DEPT') or '').strip()
        ed = str(er.get('DEPT') or '').strip()
        dept_pairs[(jd, ed)] = dept_pairs.get((jd, ed), 0) + 1
        
        jv = str(jr.get('DIV') or '').strip()
        ev = str(er.get('DIV') or '').strip()
        div_pairs[(jv, ev)] = div_pairs.get((jv, ev), 0) + 1

print("Dept mapping (JSON -> EOD):")
for (jd, ed), cnt in sorted(dept_pairs.items(), key=lambda x: -x[1]):
    print(f"  JSON {jd!r:15} -> EOD {ed!r:15}: {cnt} rows")

print("\nDiv mapping (JSON -> EOD):")
for (jv, ev), cnt in sorted(div_pairs.items(), key=lambda x: -x[1]):
    print(f"  JSON {jv!r:15} -> EOD {ev!r:15}: {cnt} rows")

