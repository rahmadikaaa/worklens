import json
from pathlib import Path

p_3456 = Path(r"C:\Users\rahma\Downloads\breakdown_activity (1).json")
p_3460 = Path(r"backend/uploads/breakdown_activity_261105_1704_1.json")

with open(p_3456, "r", encoding="utf-8") as f:
    r_3456 = json.load(f)["value"]

with open(p_3460, "r", encoding="utf-8") as f:
    d = json.load(f)
    r_3460 = d.get("value", d) if isinstance(d, dict) else d

def parse_num(v):
    if v is None: return None
    s = str(v).strip().replace(",", ".")
    try: return float(s)
    except: return None

gt_3456 = [r for r in r_3456 if parse_num(r.get("Workload")) and parse_num(r.get("Workload")) > 0]
gt_3460 = [r for r in r_3460 if parse_num(r.get("Workload")) and parse_num(r.get("Workload")) > 0]

print(f"3456 file: total={len(r_3456)}, gt_zero={len(gt_3456)}, sum_h={sum(parse_num(r['Workload'])/60 for r in gt_3456):.2f}")
print(f"3460 file: total={len(r_3460)}, gt_zero={len(gt_3460)}, sum_h={sum(parse_num(r['Workload'])/60 for r in gt_3460):.2f}")

# Find the 4 rows difference
ids_3456 = set(r.get("activity_id") for r in r_3456)
ids_3460 = set(r.get("activity_id") for r in r_3460)

diff_3460_extra = [r for r in r_3460 if r.get("activity_id") not in ids_3456]
print(f"Extra rows in 3460: {len(diff_3460_extra)}")
for r in diff_3460_extra:
    print("  Extra row:", r.get("activity_id"), "| Workload:", r.get("Workload"))

