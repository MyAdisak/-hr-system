import json, urllib.request, urllib.error

N8N_BASE = "http://hr_n8n:5678"
WORKFLOW_ID = "9kH7p3Hm9dZE3iiG"

env = {}
with open("/opt/hr-system/.env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

api_key = env["N8N_API_KEY"]
headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}

req = urllib.request.Request(f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers=headers)
with urllib.request.urlopen(req, timeout=30) as r:
    wf = json.loads(r.read())

print(f"GET ok: nodes={len(wf['nodes'])}")

# ลอง PUT โดยไม่แก้ไขอะไรก่อน เพื่อดูว่า 400 มาจากอะไร
payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], "settings": wf.get("settings", {}), "staticData": wf.get("staticData")}
body = json.dumps(payload).encode()
req2 = urllib.request.Request(f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", method="PUT", headers=headers, data=body)
try:
    with urllib.request.urlopen(req2, timeout=30) as r:
        result = json.loads(r.read())
    print(f"PUT ok: nodes={len(result['nodes'])}")
except urllib.error.HTTPError as e:
    print(f"PUT error {e.code}:")
    print(e.read().decode())
