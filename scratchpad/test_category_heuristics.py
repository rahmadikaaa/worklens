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

def predict_category_action(row):
    act = str(row.get('ACTIVITY NAME', '')).lower()
    t_act = str(row.get('TYPE ACTIVITY', '')).lower()
    
    # Check Auto Housekeeping
    if any(k in act for k in ['housekeeping', 'delete log', 'clear log', 'clear event', 'clean log', 'cleanup', 'delete file', 'remove log']):
        return 'Auto Housekeeping'
    if 'housekeeping' in t_act:
        return 'Auto Housekeeping'
        
    # Check Auto Restart
    if any(k in act for k in ['restart bot', 'cypress', 'admin api']):
        return 'Auto Restart'
        
    # Check Health Check
    if any(k in act for k in ['health check', 'healthcheck', 'cek health', 'memory usage', 'disk usage', 'cpu usage']):
        return 'Health Check'
        
    # Check Auto Monitoring
    if any(k in act for k in ['monitoring', 'grafana', 'widget', 'traffic', 'success rate', 'error count', 'view dashboard', 'dashboard']):
        return 'Auto Monitoring'
    if 'monitoring' in t_act:
        return 'Auto Monitoring'
        
    # Check Smart Healing
    if any(k in act for k in ['restart', 'start stop', 'reboot', 'kill', 'recycle', 'stop and start', 'service restart']):
        return 'Smart Healing'
        
    # Check Self Service Request
    if any(k in act for k in ['order', 'ticket', 'subscriber', 'check log', 'finding', 'how to get', 'whitelist', 'query', 'unblock', 'esim', 'fmc', 'create']):
        return 'Self Service Request'
    if 'service request' in t_act:
        return 'Self Service Request'
        
    return 'Smart Healing'

preds = merged.apply(predict_category_action, axis=1)
acc = (preds == merged['Category Action_csv']).mean()
print(f"Accuracy: {acc*100:.2f}% ({sum(preds == merged['Category Action_csv'])}/{len(merged)})")

errors = merged[preds != merged['Category Action_csv']]
print(f"Errors count: {len(errors)}")
print("Error breakdown (Actual vs Pred):")
print(pd.crosstab(errors['Category Action_csv'], preds[preds != merged['Category Action_csv']]))
