#!/usr/bin/env python3
"""
Wire AI Classify Intent into HR - LINE Bot Handler.

Strategy: AI fallback (rule-match path untouched).
  Parse LINE Event ─┬─ rule match  ─→ Lookup Employee (เดิม)
                    └─ action='unknown' ─→ Prep AI Input → AI Classify → AI Action Mapper → Lookup Employee

Run on VPS:
  docker run --rm --network=hr-system_hrnet -v /opt/hr-system/scripts:/scripts \
    -v /opt/hr-system/.env:/env -e ENV_FILE=/env \
    python:3.11-alpine sh -c 'pip install requests -q && python /scripts/wire_ai_into_line_bot.py'
"""
import json
import os
import sys
import urllib.request
import uuid

WORKFLOW_ID = "9kH7p3Hm9dZE3iiG"
AI_CLASSIFY_ID = "97lD7mqpfOyvuu6u"
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
        body = json.dumps(data).encode("utf-8")
        req.data = body
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")

def main():
    env = load_env()
    api_key = env.get("N8N_API_KEY")
    if not api_key:
        print("ERROR: N8N_API_KEY not set in .env"); sys.exit(1)

    headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}

    # 1) GET current workflow
    code, wf = http("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers)
    if code != 200:
        print(f"GET failed: {code} {wf}"); sys.exit(1)
    print(f"GET ok — name={wf['name']}, nodes={len(wf['nodes'])}")

    # Backup local copy on VPS
    backup_path = f"/scripts/line-bot-export.json.bak.beforeai"
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
    if "AI Classify" in existing_names:
        print("AI Classify already wired — abort"); sys.exit(0)

    # 2) Patch "Parse LINE Event" — push action='unknown' instead of continue
    new_parse_code = '''
const body = $input.first().json.body;
const events = body.events || [];
const results = [];

const AUTH_REQUIRED = new Set(['checkin','checkout','leave','check_time','check_leave','approve_leave','reject_leave','list_pending']);
const PUBLIC_ACTIONS = new Set(['register','add_employee','add_employee_error','help']);
const ADMIN_ONLY    = new Set(['approve_leave','reject_leave','list_pending','add_employee']);

for (const ev of events) {
  if (ev.type !== 'message' || ev.message.type !== 'text') continue;

  const sourceType  = ev.source.type;
  const lineUserId  = ev.source.userId || '';
  const groupId     = ev.source.groupId || null;
  const text        = ev.message.text.trim();
  const replyToken  = ev.replyToken;

  let action = 'skip';
  let leaveType = null, empName = null, position = null;
  let dailyWage = 0, baseSalary = 0, payType = null, empCode = null;
  let leaveId = null, leaveReason = null;

  if (/^(เข้า|เข้างาน|checkin|check in|in)$/i.test(text))            { action = 'checkin'; }
  else if (/^(ออก|ออกงาน|checkout|check out|out)$/i.test(text))       { action = 'checkout'; }
  else if (/ลาป่วย|sick/i.test(text))                                  { action = 'leave'; leaveType = 'sick'; }
  else if (/ลาพักร้อน|ลาพัก|annual/i.test(text))                      { action = 'leave'; leaveType = 'annual'; }
  else if (/ลากิจ|personal/i.test(text))                              { action = 'leave'; leaveType = 'personal'; }
  else if (/^(สวัสดี|hello|hi|^help$|ช่วยด้วย|เมนู|menu|คำสั่ง)$/i.test(text)) { action = 'help'; }
  else if (/^อนุมัติ\\s+(\\d+)\\s*$/i.test(text)) {
    const m = text.match(/^อนุมัติ\\s+(\\d+)\\s*$/i);
    action = 'approve_leave'; leaveId = parseInt(m[1]);
  }
  else if (/^ปฏิเสธ\\s+(\\d+)(?:\\s+(.+))?$/i.test(text)) {
    const m = text.match(/^ปฏิเสธ\\s+(\\d+)(?:\\s+(.+))?$/i);
    action = 'reject_leave'; leaveId = parseInt(m[1]);
    leaveReason = (m[2] || '').trim() || null;
  }
  else if (/^(ใบลารอ|รายการลา|ลาที่รออนุมัติ)$/i.test(text)) { action = 'list_pending'; }
  else if (/^เพิ่ม/i.test(text)) {
    const m = text.match(/^เพิ่ม(.+?)\\s+ตำแหน่ง(.+?)\\s+(รายวัน|รายเดือน)\\s+(?:วันละ|เดือนละ)\\s*(\\d+(?:\\.\\d+)?)/i);
    if (m) {
      action = 'add_employee';
      empName  = m[1].trim(); position = m[2].trim();
      payType  = m[3] === 'รายวัน' ? 'daily' : 'monthly';
      const amt = parseFloat(m[4]);
      if (payType === 'daily') dailyWage = amt; else baseSalary = amt;
    } else { action = 'add_employee_error'; }
  }
  else if (/^ลงทะเบียน\\s+(\\S+)/i.test(text)) {
    const m = text.match(/^ลงทะเบียน\\s+(\\S+)/i);
    empCode = m[1].trim().toUpperCase();
    action = 'register';
  }
  else if (/^(ดูเวลา|เวลาเข้า|เวลาออก|ดูการเข้างาน|เวลา)$/i.test(text)) { action = 'check_time'; }
  else if (/^(ดูการลา|สถานะลา|ใบลา|ดูใบลา)$/i.test(text))             { action = 'check_leave'; }

  // Text no-match → mark 'unknown' so AI fallback path can pick it up
  if (action === 'skip') action = 'unknown';

  results.push({ json: {
    lineUserId, groupId, sourceType, text, action, leaveType, replyToken,
    empName, position, payType, dailyWage, baseSalary, empCode,
    leaveId, leaveReason,
    needsAuth: AUTH_REQUIRED.has(action),
    isPublic:  PUBLIC_ACTIONS.has(action),
    adminOnly: ADMIN_ONLY.has(action)
  }});
}

if (results.length === 0) return [{ json: { action: 'skip', lineUserId: '', replyToken: '' } }];
return results;
'''
    parse_node = next(n for n in nodes if n["name"] == "Parse LINE Event")
    parse_node["parameters"]["jsCode"] = new_parse_code
    print("patched: Parse LINE Event (continue → push 'unknown')")

    # 3) New nodes
    base_x = 480  # original Parse LINE Event x ~440? we'll fit between
    base_y = 280

    # Find positions for layout (rough)
    parse_pos = parse_node.get("position", [440, 300])
    px, py = parse_pos[0], parse_pos[1]

    is_unknown = {
        "id": str(uuid.uuid4()),
        "name": "Is Unknown",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [px + 220, py],
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "combinator": "and",
                "conditions": [{
                    "id": "c1",
                    "leftValue": "={{ $json.action }}",
                    "rightValue": "unknown",
                    "operator": {"type": "string", "operation": "equals"}
                }]
            },
            "options": {}
        }
    }

    prep_ai = {
        "id": str(uuid.uuid4()),
        "name": "Prep AI Input",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": [px + 440, py - 120],
        "parameters": {
            "assignments": {
                "assignments": [
                    {"id": "u1", "name": "user_msg", "value": "={{ $json.text }}", "type": "string"},
                    {"id": "u2", "name": "user_id", "value": "={{ $json.lineUserId }}", "type": "string"}
                ]
            },
            "options": {}
        }
    }

    ai_classify = {
        "id": str(uuid.uuid4()),
        "name": "AI Classify",
        "type": "n8n-nodes-base.executeWorkflow",
        "typeVersion": 1.2,
        "position": [px + 660, py - 120],
        "parameters": {
            "source": "database",
            "workflowId": {"__rl": True, "value": AI_CLASSIFY_ID, "mode": "id"},
            "workflowInputs": {
                "mappingMode": "defineBelow",
                "value": {
                    "user_msg": "={{ $json.user_msg }}",
                    "user_id": "={{ $json.user_id }}"
                }
            },
            "options": {}
        }
    }

    ai_mapper_code = '''
// Combine AI result with original LINE context, then map intent → action
const ai = $input.item.json || {};
const lineCtx = $('Parse LINE Event').item.json || {};

const intent = ai.intent || 'unknown';
const conf = (typeof ai.confidence === 'number') ? ai.confidence : 0;
const slots = ai.slots || {};

const AUTH_REQUIRED = new Set(['checkin','checkout','leave','check_time','check_leave','approve_leave','reject_leave','list_pending']);
const PUBLIC_ACTIONS = new Set(['register','add_employee','add_employee_error','help']);
const ADMIN_ONLY    = new Set(['approve_leave','reject_leave','list_pending','add_employee']);

let action = 'help';
let leaveType = null, empCode = null, leaveId = null, leaveReason = null;

if (conf < 0.5) {
  action = 'help';
} else if (intent === 'check_in') {
  action = 'checkin';
} else if (intent === 'check_out') {
  action = 'checkout';
} else if (intent === 'leave_request') {
  action = 'leave';
  leaveType = slots.leave_type || 'personal';
} else if (intent === 'register') {
  action = 'register';
  empCode = String(slots.emp_code || '').toUpperCase() || null;
} else if (intent === 'help') {
  action = 'help';
} else if (intent === 'salary_inquiry') {
  action = 'help';
} else if (typeof intent === 'string' && intent.startsWith('admin_mark_')) {
  action = 'help';
} else {
  action = 'help';
}

return [{ json: {
  lineUserId: lineCtx.lineUserId,
  groupId: lineCtx.groupId,
  sourceType: lineCtx.sourceType,
  text: lineCtx.text,
  replyToken: lineCtx.replyToken,
  action,
  leaveType,
  empName: null,
  position: null,
  payType: null,
  dailyWage: 0,
  baseSalary: 0,
  empCode,
  leaveId,
  leaveReason,
  needsAuth: AUTH_REQUIRED.has(action),
  isPublic: PUBLIC_ACTIONS.has(action),
  adminOnly: ADMIN_ONLY.has(action),
  ai_intent: intent,
  ai_confidence: conf
}}];
'''
    ai_mapper = {
        "id": str(uuid.uuid4()),
        "name": "AI Action Mapper",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [px + 880, py - 120],
        "parameters": {"jsCode": ai_mapper_code}
    }

    nodes.extend([is_unknown, prep_ai, ai_classify, ai_mapper])
    print("added 4 nodes: Is Unknown, Prep AI Input, AI Classify, AI Action Mapper")

    # 4) Rewire connections
    # Old: Parse LINE Event → Lookup Employee
    # New:
    #   Parse LINE Event → Is Unknown
    #   Is Unknown[true] → Prep AI Input → AI Classify → AI Action Mapper → Lookup Employee
    #   Is Unknown[false] → Lookup Employee
    conns["Parse LINE Event"] = {"main": [[{"node": "Is Unknown", "type": "main", "index": 0}]]}
    conns["Is Unknown"] = {"main": [
        [{"node": "Prep AI Input", "type": "main", "index": 0}],   # output 0 = true
        [{"node": "Lookup Employee", "type": "main", "index": 0}]  # output 1 = false
    ]}
    conns["Prep AI Input"] = {"main": [[{"node": "AI Classify", "type": "main", "index": 0}]]}
    conns["AI Classify"] = {"main": [[{"node": "AI Action Mapper", "type": "main", "index": 0}]]}
    conns["AI Action Mapper"] = {"main": [[{"node": "Lookup Employee", "type": "main", "index": 0}]]}
    print("rewired: connections")

    # 5) PUT workflow (n8n API requires only specific fields)
    payload = {
        "name": wf["name"],
        "nodes": nodes,
        "connections": conns,
        "settings": wf.get("settings", {})
    }
    code, resp = http("PUT", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers, payload)
    if code != 200:
        print(f"PUT failed: {code} {resp}"); sys.exit(1)
    print(f"PUT ok — workflow updated, nodes now = {len(resp['nodes'])}")

    # Verify still active
    code, after = http("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers)
    if code == 200:
        if not after.get("active"):
            print("workflow inactive after PUT — re-activating")
            code2, _ = http("POST", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}/activate", headers, {})
            print(f"activate result: {code2}")
        else:
            print("workflow still active ✓")
    print("DONE")

if __name__ == "__main__":
    main()
