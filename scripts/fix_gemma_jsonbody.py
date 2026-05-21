#!/usr/bin/env python3
"""
Fix Gemma sub-workflow HTTP node: jsonBody เขียนแบบ `={ ... + JS concat ... }`
ที่ n8n ไม่ evaluate operator outside {{ }} → JSON.parse fail.

Refactor: แยก prompt building เป็น Code node ก่อน HTTP, then HTTP body = `={{ JSON.stringify($json.body) }}`

Targets: 97lD7mqpfOyvuu6u (Classify), sF2057d0TJUkiTQT (Format Thai)
"""
import json
import os
import sys
import urllib.request
import uuid

N8N_BASE = "http://hr_n8n:5678"
CLASSIFY_ID = "97lD7mqpfOyvuu6u"
FORMAT_ID = "sF2057d0TJUkiTQT"

CLASSIFY_PROMPT = '''You classify Thai HR LINE messages. Output ONLY a single JSON object on one line. No prose, no markdown, no code fences.
Schema: {"intent": one of [check_in, check_out, leave_request, salary_inquiry, ot_request, register, help, admin_mark_leave, admin_mark_absent, admin_mark_half_morning, admin_mark_half_afternoon, unknown], "confidence": 0-1, "slots": {"emp_name"?: string, "date_start"?: YYYY-MM-DD, "date_end"?: YYYY-MM-DD, "leave_type"?: one of [sick, annual, personal, other], "reason"?: string, "emp_code"?: string}}

Resolve relative Thai dates using current_date below.
- วันนี้ = current_date
- พรุ่งนี้ = current_date + 1 day
- มะรืน/มะรืนนี้ = current_date + 2 days
- เมื่อวาน/เมื่อวานนี้ = current_date - 1 day
- ถ้าระบุแค่ '12/5' หรือ '12 พ.ค.' ให้ใช้ปีของ current_date

Admin commands (ผู้ส่งเป็นแอดมินแจ้งคนอื่นลา/ขาด/ครึ่งวัน):
- 'พรุ่งนี้จ๊อดลาป่วย' → admin_mark_leave, slots:{emp_name:'จ๊อด', date_start:tomorrow, leave_type:'sick'}
- 'เขียวลาพักร้อน 10-12 พฤษภา' → admin_mark_leave, slots:{emp_name:'เขียว', date_start:'2026-05-10', date_end:'2026-05-12', leave_type:'annual'}
- 'หมวยขาด' → admin_mark_absent, slots:{emp_name:'หมวย', date_start:today}
- 'ทองครึ่งเช้า' → admin_mark_half_morning, slots:{emp_name:'ทอง', date_start:today}
- 'ลายครึ่งบ่ายวันนี้' → admin_mark_half_afternoon, slots:{emp_name:'ลาย', date_start:today}

Employee self-service:
- 'ลาป่วยพรุ่งนี้' → leave_request, slots:{leave_type:'sick', date_start:tomorrow}
- 'เงินเดือน' → salary_inquiry
- 'ลงทะเบียน EMP005' → register, slots:{emp_code:'EMP005'}

If unclear or off-topic, use intent='unknown' with low confidence.
'''

FORMAT_PROMPT = '''You rewrite text into polite, concise Thai suitable for HR LINE replies. Output ONLY a single JSON object on one line. No prose, no markdown, no code fences.
Schema: {"formatted": "..."}
Respect tone and max_chars from input if provided.
- tone='polite' → ใช้ค่ะ/ครับ
- tone='neutral' → ตรงประเด็น ไม่ต้องสุภาพมาก
- max_chars → ไม่เกินจำนวน chars นี้
Default tone=polite, max_chars=200
'''


def load_env():
    path = os.environ.get("ENV_FILE", "/env")
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
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


def make_build_body_classify():
    # Code node JS that constructs body object
    return '''
const userMsg = $json.user_msg || '';
const today = new Date().toISOString().slice(0,10);
const systemPrompt = ''' + json.dumps(CLASSIFY_PROMPT, ensure_ascii=False) + ''' + "\\ncurrent_date: " + today + "\\nInput: " + JSON.stringify(userMsg) + "\\n\\nJSON:";

const body = {
  contents: [{ role: 'user', parts: [{ text: systemPrompt }] }],
  generationConfig: { maxOutputTokens: 300, temperature: 0.1 }
};
return [{ json: { body, user_msg: userMsg, user_id: $json.user_id } }];
'''.lstrip()


def make_build_body_format():
    return '''
const raw = $json.raw_text || '';
const tone = $json.tone || 'polite';
const maxChars = $json.max_chars || 200;
const systemPrompt = ''' + json.dumps(FORMAT_PROMPT, ensure_ascii=False) + ''' + "\\nInput: " + JSON.stringify({raw_text: raw, tone, max_chars: maxChars}) + "\\n\\nJSON:";

const body = {
  contents: [{ role: 'user', parts: [{ text: systemPrompt }] }],
  generationConfig: { maxOutputTokens: 400, temperature: 0.1 }
};
return [{ json: { body } }];
'''.lstrip()


def patch_workflow(wf_id, http_node_name, build_code, headers):
    code, wf = http("GET", f"{N8N_BASE}/api/v1/workflows/{wf_id}", headers)
    if code != 200:
        print(f"GET {wf_id} failed: {code} {wf}"); return False
    print(f"GET {wf['name']} ok — nodes={len(wf['nodes'])}")

    nodes = wf["nodes"]
    conns = wf["connections"]

    # Idempotency
    if any(n["name"] == "Build Body" for n in nodes):
        print("Build Body node exists already → only patching HTTP body + connections")

    # Find HTTP node
    http_node = next((n for n in nodes if n["name"] == http_node_name), None)
    if not http_node:
        print(f"HTTP node '{http_node_name}' not found"); return False

    # Find upstream node connecting to HTTP node (Filter Payload typically)
    upstream_name = None
    for src, c in conns.items():
        for branch in c.get("main", []):
            for tgt in branch:
                if tgt.get("node") == http_node_name:
                    upstream_name = src; break
    print(f"upstream of {http_node_name} = {upstream_name}")
    if not upstream_name:
        print("can't find upstream"); return False

    # Add Build Body node (Code) if not present
    build_node = next((n for n in nodes if n["name"] == "Build Body"), None)
    if not build_node:
        up = next(n for n in nodes if n["name"] == upstream_name)
        bx, by = up.get("position", [400, 300])
        build_node = {
            "id": str(uuid.uuid4()),
            "name": "Build Body",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [bx + 200, by],
            "parameters": {"jsCode": build_code}
        }
        nodes.append(build_node)
        # Shift http node right
        hx, hy = http_node.get("position", [600, 300])
        http_node["position"] = [hx + 200, hy]
        print("added Build Body node")
    else:
        build_node["parameters"]["jsCode"] = build_code
        print("updated Build Body node code")

    # Patch HTTP node — body uses $json.body
    http_node["parameters"]["jsonBody"] = "={{ JSON.stringify($json.body) }}"
    http_node["parameters"]["specifyBody"] = "json"
    print(f"patched {http_node_name} jsonBody")

    # Reconnect: upstream → Build Body → HTTP
    conns[upstream_name] = {"main": [[{"node": "Build Body", "type": "main", "index": 0}]]}
    conns["Build Body"] = {"main": [[{"node": http_node_name, "type": "main", "index": 0}]]}
    print("rewired connections")

    payload = {
        "name": wf["name"],
        "nodes": nodes,
        "connections": conns,
        "settings": wf.get("settings", {})
    }
    code, resp = http("PUT", f"{N8N_BASE}/api/v1/workflows/{wf_id}", headers, payload)
    if code != 200:
        print(f"PUT failed: {code} {resp}"); return False
    print(f"PUT {wf_id} ok — nodes now = {len(resp['nodes'])}")

    # Verify active
    code, after = http("GET", f"{N8N_BASE}/api/v1/workflows/{wf_id}", headers)
    if code == 200 and not after.get("active"):
        code2, _ = http("POST", f"{N8N_BASE}/api/v1/workflows/{wf_id}/activate", headers, {})
        print(f"reactivated: {code2}")
    return True


def main():
    env = load_env()
    api_key = env.get("N8N_API_KEY")
    if not api_key: sys.exit("N8N_API_KEY missing")
    headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}

    print("==== Patching Classify ====")
    if not patch_workflow(CLASSIFY_ID, "Gemma - Classify", make_build_body_classify(), headers):
        sys.exit(1)

    print("\n==== Patching Format Thai ====")
    if not patch_workflow(FORMAT_ID, "Gemma - Format", make_build_body_format(), headers):
        # Try common name variants
        if not patch_workflow(FORMAT_ID, "Gemma - Format Thai", make_build_body_format(), headers):
            print("(format Thai HTTP node name unknown — check manually)")

    print("\nDONE")


if __name__ == "__main__":
    main()
