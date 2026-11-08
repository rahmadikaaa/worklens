import pandas as pd
import sys
sys.path.append(r'C:\Users\rahma\OneDrive\Documents\worklens')
from backend.app.services.discovery_service import generate_canonical_benefit

csv_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'
df_csv = pd.read_csv(csv_path)

def clean_num(val):
    if val is None or pd.isna(val): return 0.0
    import re
    s = str(val).strip().replace(',', '.')
    m = re.search(r'^-?\d+(?:\.\d+)?', s)
    return float(m.group(0)) if m else 0.0

matches_with_cicd_rule = 0
matches_without_cicd_rule = 0

for idx, r in df_csv.iterrows():
    dur = clean_num(r['Durasi (Menit)'])
    ev = clean_num(r['Event Per Month'])
    wl = clean_num(r['Workload'])
    cat = r['Category Action']
    tool = r['Tools Automation']
    st = r['Status Triggered']
    actual_ben = r['Benefit'].strip()
    
    # with rule
    gen1 = generate_canonical_benefit(cat, tool, st, dur, ev, wl)
    if gen1 == actual_ben:
        matches_with_cicd_rule += 1
    else:
        print(f"Diff with rule on row {idx} ({r['CONCAT']}):")
        print(f"  ACTUAL: {actual_ben}")
        print(f"  GEN   : {gen1}")
        
    # without rule (just via {tool})
    # if tool == 'CICD' it would be 'via CICD'
    # let's see how many have tool == 'CICD':

print(f"Matches with CI/CD rule: {matches_with_cicd_rule}/{len(df_csv)}")
print(f"Rows with tool == 'CICD': {sum(df_csv['Tools Automation'] == 'CICD')}")
print(f"Matches without CI/CD rule: {len(df_csv) - sum(df_csv['Tools Automation'] == 'CICD')}")

