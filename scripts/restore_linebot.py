import json, urllib.request, os, sys
N8N_BASE = "http://hr_n8n:5678"
WORKFLOW_ID = "9kH7p3Hm9dZE3iiG"
BACKUP = "/scripts/line-bot-export.json.bak.beforeformat"
env = {}
with open("/opt/hr-system/.env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
api_key = env.get("N8N_API_KEY")
with open(BACKUP) as f:
    wf = json.load(f)
print(f"Restoring: nodes={len(wf['nodes'])}")
headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}
payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf.get("settings", {}), "staticData": wf.get("staticData")}
body = json.dumps(payload).encode()
req = urllib.request.Request(f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", method="PUT", headers=headers, data=body)
with urllib.request.urlopen(req, timeout=30) as r:
    result = json.loads(r.read())
print(f"Done: nodes={len(result['nodes'])}, active={result['active']}")
