import json, urllib.request, urllib.error, uuid

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

# Find Do Check-in and Reply Check-in positions
node_map = {n["name"]: n for n in wf["nodes"]}
do_ci = node_map.get("Do Check-in")
reply_ci = node_map.get("Reply Check-in")

if not do_ci or not reply_ci:
    print("ERROR: nodes not found"); exit(1)

# Add Set node between Do Check-in and Reply Check-in
set_node_id = str(uuid.uuid4())
rx, ry = reply_ci["position"]
set_node = {
    "id": set_node_id,
    "name": "Prep Reply Token",
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [rx - 200, ry],
    "parameters": {
        "mode": "keepAllExcept",
        "fields": {"values": []},
        "options": {},
        "assignments": {
            "assignments": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "replyToken",
                    "value": "={{ $('Merge Data').first().json.replyToken }}",
                    "type": "string"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "full_name",
                    "value": "={{ $('Merge Data').first().json.full_name }}",
                    "type": "string"
                }
            ]
        }
    }
}

wf["nodes"].append(set_node)

# Rewire: Do Check-in -> Prep Reply Token -> Reply Check-in
conns = wf["connections"]

# Find and update connection from Do Check-in to Reply Check-in
if "Do Check-in" in conns:
    for port, dest_lists in conns["Do Check-in"].items():
        for dest_list in dest_lists:
            for dest in dest_list:
                if dest["node"] == "Reply Check-in":
                    dest["node"] = "Prep Reply Token"

# Add Prep Reply Token -> Reply Check-in
conns["Prep Reply Token"] = {"main": [[{"node": "Reply Check-in", "type": "main", "index": 0}]]}

# Update Reply Check-in replyToken expression to use direct field
reply_ci["parameters"]["replyToken"] = "={{ $json.replyToken }}"
reply_ci["parameters"]["messages"] = [{"type": "text", "text": "={{ '✅ ' + $json.full_name + ' เข้างานแล้วครับ' }}"}]

print(f"Added Prep Reply Token node")

payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": {"executionOrder": "v1"},
    "staticData": wf.get("staticData"),
}
body = json.dumps(payload).encode()
req2 = urllib.request.Request(f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", method="PUT", headers=headers, data=body)
try:
    with urllib.request.urlopen(req2, timeout=30) as r:
        result = json.loads(r.read())
    print(f"Done: nodes={len(result['nodes'])}, active={result['active']}")
except urllib.error.HTTPError as e:
    print(f"PUT error {e.code}: {e.read().decode()[:500]}")
