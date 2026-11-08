import pandas as pd
import json

csv_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'
json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'

df_csv = pd.read_csv(csv_path)
with open(json_path, 'r', encoding='utf-8') as f:
    raw_json = json.load(f)['value']
df_json = pd.DataFrame(raw_json)

df_csv['concat_clean'] = df_csv['CONCAT'].str.strip()
df_json['concat_clean'] = df_json['CONCAT'].str.strip()

merged = pd.merge(df_csv, df_json, on='concat_clean', suffixes=('_csv', '_json'))

# Let's inspect the actual Category Action vs TYPE ACTIVITY and keywords
# Specifically, what does TYPE ACTIVITY say?
for ca, grp in merged.groupby('Category Action_csv'):
    print(f"\n--- {ca} ({len(grp)}) ---")
    print("TYPE ACTIVITY:", grp['TYPE ACTIVITY'].value_counts().to_dict())
    print("Sample activity names:", grp['ACTIVITY NAME'].head(5).tolist())

