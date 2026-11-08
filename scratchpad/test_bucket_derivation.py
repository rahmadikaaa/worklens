import json
from pathlib import Path
from collections import Counter

p = Path(r"backend/uploads/breakdown_activity_261105_1704_1.json")
with open(p, "r", encoding="utf-8") as f:
    raw = json.load(f)

rows = raw.get("value", raw) if isinstance(raw, dict) else raw

def parse_num(v):
    if v is None: return None
    s = str(v).strip().replace(",", ".")
    try: return float(s)
    except: return None

gt_zero = [r for r in rows if parse_num(r.get("Workload")) and parse_num(r.get("Workload")) > 0]

def get_bucket(r):
    st = str(r.get("Status") or "").strip().lower().replace(" ", "")
    cn = str(r.get("Category Notes") or "").strip()
    
    if st == "takeout":
        return "Take Out"
    if cn == "Not Possible Automate":
        return "Tidak mungkin diotomasi"
    if cn == "Already Automation":
        return "Sudah diotomasi"
    if cn == "Dismantled":
        return "Dismantled"
    if cn in ["To Be Automated", "As Is", "Not Yet Solution", "Need Further Assessment", "Already Automated"]:
        return "Kandidat"
    return "Lainnya"

bucket_counts = Counter()
bucket_hours = Counter()

for r in gt_zero:
    b = get_bucket(r)
    wl = parse_num(r.get("Workload"))
    bucket_counts[b] += 1
    bucket_hours[b] += wl / 60.0

print("Derived Bucket Counts:")
for b in ["Dismantled", "Kandidat", "Lainnya", "Sudah diotomasi", "Take Out", "Tidak mungkin diotomasi"]:
    print(f"  {b}: n={bucket_counts[b]}, h={bucket_hours[b]:.1f}")

print("\nPrototype Buckets:")
print("  Dismantled: n=63, h=171.3")
print("  Kandidat: n=200, h=357.5")
print("  Lainnya: n=0, h=0.0")
print("  Sudah diotomasi: n=954, h=1993.7")
print("  Take Out: n=80, h=267.6")
print("  Tidak mungkin diotomasi: n=178, h=811.9")
