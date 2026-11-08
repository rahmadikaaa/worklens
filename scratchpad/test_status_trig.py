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

# If we predict using predicted Tool and predicted Category Action, and assume a status:
# Let's see: what if status is assumed 'Not Yet Triggered Automated'?
# Or what if status is predicted from heuristics?
print("Status Triggered counts in CSV:")
print(df_csv['Status Triggered'].value_counts())

