import pandas as pd
import json

json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'
csv_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'

with open(json_path, 'r', encoding='utf-8') as f:
    raw_json = json.load(f)['value']

df_json = pd.DataFrame(raw_json)
df_csv = pd.read_csv(csv_path)

# Let's inspect rows with Workload == 0 in CSV
sima = df_csv[df_csv['CONCAT'].str.contains('SIMA', na=False)]
print("SIMA rows in CSV:")
for idx, r in sima.iterrows():
    print(r.to_dict())

print("\nSIMA rows in JSON:")
sima_json = df_json[df_json['CONCAT'].str.contains('SIMA', na=False)]
for idx, r in sima_json.iterrows():
    print(r['CONCAT'], "|", r['Durasi (Menit)'], "|", r['Event Per Month'], "|", r['Workload'])

