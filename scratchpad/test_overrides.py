import json, csv

with open(r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json', 'r', encoding='utf-8') as f:
    json_rows = json.load(f)['value']
with open(r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv', 'r', encoding='utf-8', errors='ignore') as f:
    benefit_rows = list(csv.DictReader(f))

json_by_c = {str(r.get('CONCAT') or '').strip(): r for r in json_rows}
benefit_by_c = {str(r.get('CONCAT') or '').strip(): r for r in benefit_rows}

for target in ['Email Relay External - Housekeeping', 'Elisa - Check Log Elisa di DB']:
    jr = json_by_c.get(target)
    br = benefit_by_c.get(target)
    print(f"Target: {target}")
    if jr:
        print(f"  JSON: Durasi={jr.get('Durasi (Menit)')}, Event={jr.get('Event Per Month')}, Workload={jr.get('Workload')}")
    else:
        print("  JSON: NOT FOUND")
    if br:
        print(f"  CSV : Durasi={br.get('Durasi (Menit)')}, Event={br.get('Event Per Month')}, Workload={br.get('Workload')}")
    else:
        print("  CSV : NOT FOUND")

