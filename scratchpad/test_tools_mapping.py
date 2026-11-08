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

# In JSON: Tools Automation vs CSV: Tools Automation
print("CSV Tools Automation:")
print(df_csv['Tools Automation'].value_counts())
print("\nJSON Tools Automation:")
print(merged['Tools Automation_json'].value_counts())

# Test baseline matching:
raw_match = (merged['Tools Automation_json'] == merged['Tools Automation_csv']).mean()
print(f"Raw match: {raw_match*100:.2f}% ({sum(merged['Tools Automation_json'] == merged['Tools Automation_csv'])}/{len(merged)})")

# Apply rules:
# 1. Title case: 'Shell script' -> 'Shell Script'
# 2. 'Not Automate' -> 'AION'
# 3. What else?
def predict_tool(row):
    t = str(row.get('Tools Automation_json', '')).strip()
    act = str(row.get('ACTIVITY NAME', '')).lower()
    if t.lower() == 'shell script':
        # What if it's Grafana?
        if 'grafana' in act:
            return 'Grafana'
        return 'Shell Script'
    if t == 'Not Automate':
        if 'grafana' in act:
            return 'Grafana'
        return 'AION'
    return t

preds_tool = merged.apply(predict_tool, axis=1)
tool_acc = (preds_tool == merged['Tools Automation_csv']).mean()
print(f"Predicted tool accuracy: {tool_acc*100:.2f}% ({sum(preds_tool == merged['Tools Automation_csv'])}/{len(merged)})")

diffs = merged[preds_tool != merged['Tools Automation_csv']]
print(f"Differences ({len(diffs)}):")
for idx, r in diffs.iterrows():
    print(f"  {r['concat_clean']} | JSON: {r['Tools Automation_json']} | CSV: {r['Tools Automation_csv']} | Pred: {preds_tool[idx]}")

