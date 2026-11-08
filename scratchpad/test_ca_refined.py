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

def predict_ca(row):
    t_act = str(row.get('TYPE ACTIVITY', '')).strip()
    act = str(row.get('ACTIVITY NAME', '')).strip().lower()
    
    # 1. Housekeeping
    if t_act == 'Housekeeping' or any(k in act for k in ['housekeeping', 'clear log', 'delete log', 'clear event', 'clean log', 'cleanup']):
        return 'Auto Housekeeping'
        
    # 2. Service Request & Complaint Handling & Change Management -> Self Service Request
    if t_act in ['Service Request', 'Complaint Handling', 'Change Management']:
        # Exception: some monitoring SR?
        return 'Self Service Request'
        
    # 3. Auto Restart (specific bot/cypress/admin api)
    if any(k in act for k in ['restart bot', 'running manual bot', 'restart service cypress', 'restart admin api']):
        return 'Auto Restart'
        
    # 4. Health Check
    if any(k in act for k in ['check process', 'check service', 'check memory', 'health check', 'healthcheck', 'check disk', 'storage usage', 'cpu usage']):
        return 'Health Check'
        
    # 5. Monitoring
    if t_act in ['Daily Activity', 'Monitoring and Alerting'] or any(k in act for k in ['monitoring', 'grafana', 'traffic', 'success rate', 'error count', 'trend error']):
        return 'Auto Monitoring'
        
    # 6. Incident Handling -> Smart Healing
    if t_act == 'Incident Handling' or any(k in act for k in ['restart', 'start stop', 'reboot', 'kill', 'recycle', 'stop and start']):
        return 'Smart Healing'
        
    return 'Smart Healing'

preds = merged.apply(predict_ca, axis=1)
acc = (preds == merged['Category Action_csv']).mean()
print(f"Refined Accuracy: {acc*100:.2f}% ({sum(preds == merged['Category Action_csv'])}/{len(merged)})")
errors = merged[preds != merged['Category Action_csv']]
print(f"Errors count: {len(errors)}")
print("Error breakdown:")
for idx, r in errors.head(15).iterrows():
    print(f"  {r['CONCAT_csv']} | Act: {r['ACTIVITY NAME']} | Type: {r['TYPE ACTIVITY']} | Actual: {r['Category Action_csv']} | Pred: {preds[idx]}")

