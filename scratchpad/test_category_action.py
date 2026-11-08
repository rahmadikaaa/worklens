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

print("CSV Category Action value counts:")
print(df_csv['Category Action'].value_counts())

print("\nCross-tabulation with TYPE ACTIVITY:")
print(pd.crosstab(merged['Category Action_csv'], merged['TYPE ACTIVITY']))
