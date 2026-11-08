import json
import pandas as pd

json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'
with open(json_path, 'r', encoding='utf-8') as f:
    raw_json = json.load(f)['value']

df = pd.DataFrame(raw_json)

# Find rows containing C2P MASSTOOL or Tselid Clicker
m1 = df[df['CONCAT'].str.contains('C2P.*MASSTOOL', case=False, na=False)]
print("C2P MASSTOOL:")
for idx, r in m1.iterrows():
    print(r['CONCAT'], "|", r['Improvement Category'], "|", r['Category Notes'], "|", r['Additional Notes'], "|", r['Durasi (Menit)'], "|", r['Event Per Month'], "|", r['Workload'])

m2 = df[df['CONCAT'].str.contains('Tselid Clicker', case=False, na=False)]
print("\nTselid Clicker:")
for idx, r in m2.iterrows():
    print(r['CONCAT'], "|", r['Improvement Category'], "|", r['Category Notes'], "|", r['Additional Notes'], "|", r['Durasi (Menit)'], "|", r['Event Per Month'], "|", r['Workload'])

