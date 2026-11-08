import json
from pathlib import Path
from collections import Counter, defaultdict

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

print("=== 1. TYPES BREAKDOWN ===")
types_h = defaultdict(float)
for r in gt_zero:
    t = r.get("TYPE ACTIVITY") or "Unknown"
    wl = parse_num(r.get("Workload"))
    types_h[t] += wl / 60.0

for t, h in sorted(types_h.items(), key=lambda x: x[1], reverse=True):
    print(f"  {t}: {h:.1f} jam")

print("\n=== 2. TOOLS BREAKDOWN (Tools Automation vs Tools) ===")
tools_auto_h = defaultdict(float)
for r in gt_zero:
    tool = r.get("Tools Automation") or "Unknown"
    wl = parse_num(r.get("Workload"))
    tools_auto_h[tool] += wl / 60.0

for tool, h in sorted(tools_auto_h.items(), key=lambda x: x[1], reverse=True)[:12]:
    print(f"  {tool}: {h:.1f} jam")

print("\n=== 3. TEAMS BREAKDOWN ===")
teams_h = defaultdict(float)
for r in gt_zero:
    team = r.get("Team QC") or "Unknown"
    wl = parse_num(r.get("Workload"))
    teams_h[team] += wl / 60.0

for team, h in sorted(teams_h.items(), key=lambda x: x[1], reverse=True):
    print(f"  {team}: {h:.1f} jam")

print("\n=== 4. PARETO CONCENTRATION ===")
all_wl_sorted = sorted([parse_num(r.get("Workload")) / 60.0 for r in gt_zero], reverse=True)
total_h = sum(all_wl_sorted)
for n in [1, 10, 20, 50, 100, 200, 400, len(all_wl_sorted)]:
    cum = sum(all_wl_sorted[:n])
    pct = (cum / total_h) * 100.0
    print(f"  Top {n}: {cum:.1f} jam ({pct:.1f}%)")

print("\n=== 5. DATA QUALITY q METADATA ===")
# q.txt_dur, q.txt_ev, q.na_prio, q.na_div, q.after_h, q.outlier_h
# Check non-numeric Durasi and Event in ALL 3460 rows
txt_dur = 0
txt_ev = 0
na_prio = 0
na_div = 0
after_h = 0.0

for r in rows:
    dur_raw = r.get("Durasi (Menit)")
    if dur_raw is not None and str(dur_raw).strip() != "":
        if parse_num(dur_raw) is None:
            txt_dur += 1
    
    ev_raw = r.get("Event Per Month")
    if ev_raw is not None and str(ev_raw).strip() != "":
        if parse_num(ev_raw) is None:
            txt_ev += 1

    prio = r.get("APP PRIORITY")
    if prio is None or str(prio).strip() in ["", "#N/A"]:
        na_prio += 1

    div = r.get("DIV")
    if div is None or str(div).strip() in ["", "#N/A"]:
        na_div += 1

    wla = parse_num(r.get("Workload after"))
    if wla is not None:
        after_h += wla / 60.0

# Outlier check: Office 365
# In prototype: Backup OneDrive files & Solving if Mailbox or OneDrive Storage Full and Handle Users Can’t Import PST (License F3 Only)
# dur = 1440.0, ev = 19.0, wl = 27360.0 minutes -> 27360 / 60 = 456.0 hours!
print(f"Total rows in dataset: {len(rows)}")
print(f"txt_dur count: {txt_dur} (prototype: 80)")
print(f"txt_ev count: {txt_ev} (prototype: 75)")
print(f"na_prio count: {na_prio} (prototype: 48)")
print(f"na_div count: {na_div} (prototype: 5)")
print(f"after_h: {after_h:.1f} (prototype: 445.7)")
print(f"Top 1 outlier: {all_wl_sorted[0]:.1f} hours (prototype outlier_h: 456.0)")

