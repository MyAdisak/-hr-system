#!/usr/bin/env python3
"""
Wire AI Format Thai into HR - LINE Bot Handler reply nodes.

Strategy:
  Before each key reply node, insert a "Format: <ReplyName>" node that:
  1. Calls AI Format Thai sub-workflow with the raw message text
  2. Passes the formatted Thai text to the LINE reply node

  Targets: Reply Check-in, Reply Check-out, Reply Leave, Reply Help,
           Reply Not Registered, Reply Register, Reply Check Time, Reply Not Allowed

  Previous message strings become the "raw_text" input to AI Format Thai.
  Each reply node is updated to use `$json.formatted` from the format node.

Run on VPS:
  docker run --rm --network=hr-system_hrnet -v /opt/hr-system/scripts:/scripts \
    -v /opt/hr-system/.env:/env -e ENV_FILE=/env \
    python:3.11-alpine sh -c 'pip install requests -q && python /scripts/wire_ai_format_thai.py'
"""
import json
import os
import sys
import urllib.request
import uuid

WORKFLOW_ID = "9kH7p3Hm9dZE3iiG"
AI_FORMAT_ID = "sF2057d0TJUkiTQT"
N8N_BASE = "http://hr_n8n:5678"


def load_env():
    path = os.environ.get("ENV_FILE", "/env")
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def http(method, url, headers=None, data=None):
    req = urllib.request.Request(url, method=method, headers=headers or {})
    if data is not None:
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def new_id():
    return str(uuid.uuid4())


def main():
    env = load_env()
    api_key = env.get("N8N_API_KEY")
    if not api_key:
        print("ERROR: N8N_API_KEY not set"); sys.exit(1)

    headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}

    # 1) GET current workflow
    code, wf = http("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers)
    if code != 200:
        print(f"GET failed: {code} {wf}"); sys.exit(1)
    print(f"GET ok — name={wf['name']}, nodes={len(wf['nodes'])}")

    # Backup
    backup_path = "/scripts/line-bot-export.json.bak.beforeformat"
    try:
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(wf, f, ensure_ascii=False, indent=2)
        print(f"backup → {backup_path}")
    except Exception as e:
        print(f"backup skipped: {e}")

    nodes = wf["nodes"]
    conns = wf["connections"]

    # Idempotency check
    existing_names = {n["name"] for n in nodes}
    if "Format: Reply Check-in" in existing_names:
        print("AI Format already wired — abort"); sys.exit(0)

    # ----------------------------------------------------------------
    # Nodes to wire AI Format Thai before (name → raw_text expression)
    # ----------------------------------------------------------------
    TARGETS = {
        "Reply Check-in": "={{ '✅ ' + $('Merge Data').first().json.full_name + ' เข้างานแล้ว\\n🕐 ' + new Date().toLocaleTimeString('th-TH', {timeZone:'Asia/Bangkok'}) }}",
        "Reply Check-out": "={{ '👋 ' + $('Merge Data').first().json.full_name + ' ออกงานแล้ว\\n🕐 ' + new Date().toLocaleTimeString('th-TH', {timeZone:'Asia/Bangkok'}) }}",
        "Reply Leave": "={{ 'บันทึกคำขอลาแล้ว\\nประเภท: ' + ($('Merge Data').first().json.leaveType || 'personal') }}",
        "Reply Help": "=สวัสดีครับ HR Bot ยินดีให้บริการ\\nเข้างาน / ออกงาน / ลาป่วย / ลาพักร้อน / ลากิจ / เวลาฉัน / ใบลาฉัน",
        "Reply Not Registered": "=ยังไม่ได้ลงทะเบียนในระบบ กรุณาติดต่อ HR เพื่อเพิ่ม LINE ID",
        "Reply Register": "={{ $json.emp_id ? 'ลงทะเบียนสำเร็จ ' + $json.full_name + ' (' + $json.emp_code + ')' : 'ไม่พบรหัส ' + $('Merge Data').first().json.empCode }}",
        "Reply Check Time": "={{ $json.work_date ? 'การเข้างานวันนี้ของ ' + $json.full_name + ' เข้า: ' + ($json.check_in || '-') + ' ออก: ' + ($json.check_out || '-') : 'ยังไม่มีข้อมูลการเข้างานวันนี้' }}",
        "Reply Not Allowed": "=คำสั่งนี้สำหรับ admin เท่านั้น",
    }

    # Build lookup: node name → node object
    node_map = {n["name"]: n for n in nodes}

    new_nodes = []
    new_conns_patch = {}  # source_name → format_node_name (for rewiring)

    for reply_name, raw_text_expr in TARGETS.items():
        if reply_name not in node_map:
            print(f"  skip (not found): {reply_name}")
            continue

        reply_node = node_map[reply_name]
        rx, ry = reply_node["position"]
        fmt_name = f"Format: {reply_name}"

        # Insert format node to the LEFT of the reply node
        fmt_node = {
            "id": new_id(),
            "name": fmt_name,
            "type": "n8n-nodes-base.executeWorkflow",
            "typeVersion": 1.2,
            "position": [rx - 240, ry],
            "parameters": {
                "source": "database",
                "workflowId": {"__rl": True, "value": AI_FORMAT_ID, "mode": "id"},
                "workflowInputs": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "raw_text": raw_text_expr,
                        "tone": "polite",
                        "max_chars": 200,
                    },
                },
                "options": {},
            },
        }
        new_nodes.append(fmt_node)

        # Update reply node to use formatted text
        # Replace the hardcoded message with $json.formatted from format node
        reply_node["parameters"]["messages"] = json.dumps([
            {"type": "text", "text": "={{ $json.formatted || '(ไม่มีข้อความ)' }}"}
        ])

        new_conns_patch[reply_name] = fmt_name
        print(f"  planned: {fmt_name} → {reply_name}")

    # Add new format nodes to workflow
    nodes.extend(new_nodes)

    # Rewire connections: anything pointing to a target reply node
    # should now point to the format node, and format node → reply node
    for src_name, src_ports in list(conns.items()):
        for port_name, dest_lists in src_ports.items():
            for idx, dest_list in enumerate(dest_lists):
                for dest in dest_list:
                    if dest["node"] in new_conns_patch:
                        fmt_name = new_conns_patch[dest["node"]]
                        # Redirect existing edge to format node
                        dest["node"] = fmt_name
                        # Add format → reply edge
                        if fmt_name not in conns:
                            conns[fmt_name] = {}
                        if "main" not in conns[fmt_name]:
                            conns[fmt_name]["main"] = [[]]
                        conns[fmt_name]["main"][0].append({
                            "node": list(new_conns_patch.keys())[
                                list(new_conns_patch.values()).index(fmt_name)
                            ],
                            "type": "main",
                            "index": 0,
                        })

    wf["nodes"] = nodes
    wf["connections"] = conns

    # 2) PUT updated workflow
    put_payload = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData"),
    }
    code, result = http("PUT", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers, put_payload)
    if code != 200:
        print(f"PUT failed: {code}"); print(str(result)[:500]); sys.exit(1)

    actual_nodes = len(result.get("nodes", []))
    print(f"PUT ok — nodes now: {actual_nodes}")

    # 3) Verify active
    code2, wf2 = http("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers)
    if code2 == 200:
        print(f"Verify: active={wf2.get('active')}, nodes={len(wf2.get('nodes', []))}")
    print("Done ✅")


if __name__ == "__main__":
    main()
