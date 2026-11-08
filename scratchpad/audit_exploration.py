import json
from pathlib import Path
from collections import Counter

p = Path(r"C:\Users\rahma\Downloads\breakdown_activity (1).json")
with open(p, "r", encoding="utf-8") as f:
    raw = json.load(f)

rows = raw["value"]

def parse_num(v):
    if v is None: return None
    s = str(v).strip().replace(",", ".")
    try: return float(s)
    except: return None

all_wl = [(r, parse_num(r.get("Workload"))) for r in rows]
filled_wl = [(r, w) for r, w in all_wl if w is not None]

zero_wl = [(r, w) for r, w in filled_wl if w == 0]
gt_zero_wl = [(r, w) for r, w in filled_wl if w > 0]
lt_zero_wl = [(r, w) for r, w in filled_wl if w < 0]

print(f"Total filled Workload: {len(filled_wl)}")
print(f"Workload == 0: {len(zero_wl)}")
print(f"Workload > 0: {len(gt_zero_wl)}")
print(f"Workload < 0: {len(lt_zero_wl)}")
print(f"Sum of Workload > 0: {sum(w for r, w in gt_zero_wl)/60:.2f} hours")

# Now let's see how many rows have positive workload or what filter gives 1475 rows
print("\n--- Testing subsets to find 1475 rows ---")
# Could 1475 be distinct CONCAT, distinct apps, or filtered by something?
# What about breakdown_activity_261105_1704_1.json?
p_3460 = Path(r"backend/uploads/breakdown_activity_261105_1704_1.json")
if p_3460.exists():
    with open(p_3460, "r", encoding="utf-8") as f:
        raw_3460 = json.load(f)
    rows_3460 = raw_3460.get("value", raw_3460) if isinstance(raw_3460, dict) else raw_3460
    print(f"Total in 3460 file: {len(rows_3460)}")
    wl_3460 = [(r, parse_num(r.get("Workload"))) for r in rows_3460]
    filled_3460 = [(r, w) for r, w in wl_3460 if w is not None]
    print(f"Filled in 3460 file: {len(filled_3460)}")
    gt_zero_3460 = [(r, w) for r, w in filled_3460 if w > 0]
    zero_3460 = [(r, w) for r, w in filled_3460 if w == 0]
    print(f"Workload > 0 in 3460 file: {len(gt_zero_3460)}")
    print(f"Workload == 0 in 3460 file: {len(zero_3460)}")
