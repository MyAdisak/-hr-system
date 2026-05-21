import json, urllib.request, urllib.error

N8N_BASE = "http://hr_n8n:5678"

env = {}
with open("/opt/hr-system/.env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

api_key = env["N8N_API_KEY"]
headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}

workflow = {
    "name": "HR - Auto Check-in Daily",
    "nodes": [
        {
            "id": "1",
            "name": "Every Day 8AM",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [200, 300],
            "parameters": {
                "rule": {
                    "interval": [{"field": "cronExpression", "expression": "0 8 * * *"}]
                }
            }
        },
        {
            "id": "2",
            "name": "Auto Insert Attendance",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.5,
            "position": [440, 300],
            "credentials": {"postgres": {"id": "32vFzlygafyekusC", "name": "HR PostgreSQL"}},
            "parameters": {
                "operation": "executeQuery",
                "query": """INSERT INTO attendance (emp_id, work_date, check_in, check_out, status)
SELECT 
    e.emp_id,
    CURRENT_DATE,
    (CURRENT_DATE + TIME '08:00:00') AT TIME ZONE 'Asia/Bangkok' AT TIME ZONE 'UTC',
    (CURRENT_DATE + TIME '17:00:00') AT TIME ZONE 'Asia/Bangkok' AT TIME ZONE 'UTC',
    'normal'
FROM employees e
WHERE e.status = 'active'
AND NOT EXISTS (
    SELECT 1 FROM attendance a 
    WHERE a.emp_id = e.emp_id 
    AND a.work_date = CURRENT_DATE
)
RETURNING emp_id, work_date;"""
            }
        },
        {
            "id": "3",
            "name": "Log Result",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [660, 300],
            "parameters": {
                "jsCode": """const rows = $input.all();
console.log('Auto check-in: inserted ' + rows.length + ' records for ' + new Date().toLocaleDateString('th-TH'));
return rows;"""
            }
        }
    ],
    "connections": {
        "Every Day 8AM": {"main": [[{"node": "Auto Insert Attendance", "type": "main", "index": 0}]]},
        "Auto Insert Attendance": {"main": [[{"node": "Log Result", "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"}
}

body = json.dumps(workflow).encode()
req = urllib.request.Request(f"{N8N_BASE}/api/v1/workflows", method="POST", headers=headers, data=body)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read())
    wf_id = result['id']
    print(f"Created: {wf_id}")
    
    req2 = urllib.request.Request(f"{N8N_BASE}/api/v1/workflows/{wf_id}/activate", method="POST", headers=headers, data=b'{}')
    with urllib.request.urlopen(req2, timeout=30) as r:
        print("Activated! รันทุกวัน 08:00 น.")
except urllib.error.HTTPError as e:
    print(f"Error: {e.read().decode()[:300]}")
