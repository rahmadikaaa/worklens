import json
import pandas as pd
import re

json_path = r'C:\Users\rahma\Downloads\breakdown_activity_261106_1112.json'
csv_path = r'C:\Users\rahma\Downloads\Improvements_With_Benefit.csv'

with open(json_path, 'r', encoding='utf-8') as f:
    raw_json = json.load(f)['value']

df_json = pd.DataFrame(raw_json)
df_csv = pd.read_csv(csv_path)

# Let's clean numbers in JSON
def clean_num(val):
    if val is None or pd.isna(val):
        return 0.0
    s = str(val).strip().replace(',', '.')
    # check for number at start or regex
    m = re.search(r'^-?\d+(?:\.\d+)?', s)
    if m:
        try:
            return float(m.group(0))
        except:
            return 0.0
    return 0.0

df_json['event_num'] = df_json['Event Per Month'].apply(clean_num)
df_json['durasi_num'] = df_json['Durasi (Menit)'].apply(clean_num)
df_json['workload_calc'] = df_json['durasi_num'] * df_json['event_num']
df_json['concat_clean'] = df_json['CONCAT'].str.strip()
df_csv['concat_clean'] = df_csv['CONCAT'].str.strip()

csv_keys = set(df_csv['concat_clean'])

# Let's explore Category Notes, Improvement Category, Additional Notes in df_json
print("Improvement Category values for CSV rows in JSON:")
csv_in_json = df_json[df_json['concat_clean'].isin(csv_keys)]
print(csv_in_json['Improvement Category'].value_counts())

print("\nCategory Notes values for CSV rows in JSON:")
print(csv_in_json['Category Notes'].value_counts())

print("\nAdditional Notes values for CSV rows in JSON:")
print(csv_in_json['Additional Notes'].value_counts().head(20))

# Let's test the rule mentioned by user:
# Improvement Category == 'Automation', Event Per Month >= 1
# And Additional Notes contains 'Already automate' or ...
# Let's see what rule gives 650 matches and 23 extras!

# Test 1: Category Notes == 'Already Automation' or 'Already Automated'?
# Or Improvement Category == 'Automation' and ...
# Let's check rows where Improvement Category == 'Automation' and event_num >= 1:
sub = df_json[(df_json['Improvement Category'] == 'Automation') & (df_json['event_num'] >= 1)]
print(f"\nImprovement Category == 'Automation' & event_num >= 1: {len(sub)}")

# Let's inspect sub['Additional Notes']
print("Unique Additional Notes in sub:")
print(sub['Additional Notes'].value_counts())

