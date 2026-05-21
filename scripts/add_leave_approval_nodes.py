#!/usr/bin/env python3
"""
Add leave approval flow to HR - LINE Bot Handler workflow.

Adds 3 admin commands:
  - "อนุมัติ <leave_id>"           → approve_leave
  - "ปฏิเสธ <leave_id> [เหตุผล]"   → reject_leave
  - "ใบลารอ" / "รายการลา"          → list_pending

Modifies: Parse LINE Event regex, Merge Data role guard, Route outputs.
Adds:    8 new nodes (Postgres + LINE reply/push + format).
Idempotent: skips if "Approve Leave" already exists.
"""
import json
import os
import sys
import urllib.request
import uuid

API_KEY = os.environ.get("N8N_API_KEY")
WORKFLOW_ID = "9kH7p3Hm9dZE3iiG"
BASE = "http://hr_n8n:5678/api/v1"
PG_CRED = {"id": "32vFzlygafyekusC", "name": "HR PostgreSQL"}
LINE_CRED = {"id": "99ohB1QZvLsrpMOP", "name": "LINE HR Bot"}


def http(method, path, body=None):
    req = urllib.request.Request(
        f"{BASE}{path}",
        method=method,
        headers={"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"},
    )
    if body is not None:
        req.data = json.dumps(body).encode("utf-8")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def new_id():
    return str(uuid.uuid4())


# ---------- 1. Fetch ----------
wf = http("GET", f"/workflows/{WORKFLOW_ID}")
if any(n["name"] == "Approve Leave" for n in wf["nodes"]):
    print("⚠️  Approve Leave node already exists — abort (idempotent)")
    sys.exit(0)

# ---------- 2. Update Parse LINE Event jsCode ----------
new_parse_code = r"""
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
  else if (/^อนุมัติ\s+(\d+)\s*$/i.test(text)) {
    const m = text.match(/^อนุมัติ\s+(\d+)\s*$/i);
    action = 'approve_leave'; leaveId = parseInt(m[1]);
  }
  else if (/^ปฏิเสธ\s+(\d+)(?:\s+(.+))?$/i.test(text)) {
    const m = text.match(/^ปฏิเสธ\s+(\d+)(?:\s+(.+))?$/i);
    action = 'reject_leave'; leaveId = parseInt(m[1]);
    leaveReason = (m[2] || '').trim() || null;
  }
  else if (/^(ใบลารอ|รายการลา|ลาที่รออนุมัติ)$/i.test(text)) { action = 'list_pending'; }
  else if (/^เพิ่ม/i.test(text)) {
    const m = text.match(/^เพิ่ม(.+?)\s+ตำแหน่ง(.+?)\s+(รายวัน|รายเดือน)\s+(?:วันละ|เดือนละ)\s*(\d+(?:\.\d+)?)/i);
    if (m) {
      action = 'add_employee';
      empName  = m[1].trim(); position = m[2].trim();
      payType  = m[3] === 'รายวัน' ? 'daily' : 'monthly';
      const amt = parseFloat(m[4]);
      if (payType === 'daily') dailyWage = amt; else baseSalary = amt;
    } else { action = 'add_employee_error'; }
  }
  else if (/^ลงทะเบียน\s+(\S+)/i.test(text)) {
    const m = text.match(/^ลงทะเบียน\s+(\S+)/i);
    empCode = m[1].trim().toUpperCase();
    action = 'register';
  }
  else if (/^(ดูเวลา|เวลาเข้า|เวลาออก|ดูการเข้างาน|เวลา)$/i.test(text)) { action = 'check_time'; }
  else if (/^(ดูการลา|สถานะลา|ใบลา|ดูใบลา)$/i.test(text))             { action = 'check_leave'; }

  if (action === 'skip') continue;

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
"""

# ---------- 3. Update Merge Data jsCode (add role guard) ----------
new_merge_code = r"""
const lineData = $('Parse LINE Event').first().json;
const empRow   = $input.first().json;

if (lineData.action === 'skip') return [{ json: lineData }];

const out = {
  ...lineData,
  emp_id:     empRow.emp_id    || null,
  full_name:  empRow.full_name || null,
  emp_code:   empRow.emp_code  || null,
  role:       empRow.role      || null,
  registered: !!empRow.emp_id
};

// Admin guard: ถ้าคำสั่ง admin-only แต่ผู้ใช้ไม่ใช่ admin → not_allowed
if (out.adminOnly && out.role !== 'admin') {
  out.action = 'not_allowed';
}

return [{ json: out }];
"""

# ---------- 4. Apply jsCode updates ----------
for n in wf["nodes"]:
    if n["name"] == "Parse LINE Event":
        n["parameters"]["jsCode"] = new_parse_code
    elif n["name"] == "Merge Data":
        n["parameters"]["jsCode"] = new_merge_code

# ---------- 5. Add 4 outputs to Route node ----------
def rule(action_name):
    return {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "combinator": "and",
            "conditions": [{
                "leftValue": "={{ $json.action }}",
                "rightValue": action_name,
                "operator": {"type": "string", "operation": "equals"},
            }],
        },
        "renameOutput": True,
        "outputKey": action_name,
    }

for n in wf["nodes"]:
    if n["name"] == "Route":
        rules = n["parameters"]["rules"]["values"]
        existing = {r.get("outputKey") for r in rules}
        for ak in ("approve_leave", "reject_leave", "list_pending", "not_allowed"):
            if ak not in existing:
                rules.append(rule(ak))

# ---------- 6. New nodes ----------
def pg(name, pos, query):
    return {
        "id": new_id(), "name": name, "type": "n8n-nodes-base.postgres",
        "typeVersion": 2, "position": pos,
        "parameters": {"operation": "executeQuery", "query": query, "options": {}},
        "credentials": {"postgres": PG_CRED},
    }

def line_reply(name, pos, text_expr):
    return {
        "id": new_id(), "name": name,
        "type": "@aotoki/n8n-nodes-line-messaging.lineMessaging",
        "typeVersion": 1, "position": pos,
        "parameters": {
            "operation": "replyMessage",
            "replyToken": "={{ $('Merge Data').first().json.replyToken }}",
            "messages": [{"type": "text", "text": text_expr}],
        },
        "credentials": {"lineMessagingApi": LINE_CRED},
    }

def line_push(name, pos, to_expr, text_expr):
    return {
        "id": new_id(), "name": name,
        "type": "@aotoki/n8n-nodes-line-messaging.lineMessaging",
        "typeVersion": 1, "position": pos,
        "parameters": {
            "operation": "pushMessage",
            "to": to_expr,
            "messages": [{"type": "text", "text": text_expr}],
        },
        "credentials": {"lineMessagingApi": LINE_CRED},
    }

def code_node(name, pos, js):
    return {
        "id": new_id(), "name": name, "type": "n8n-nodes-base.code",
        "typeVersion": 2, "position": pos,
        "parameters": {"jsCode": js},
    }

# Approve: UPDATE + JOIN to fetch requester info for push
approve_sql = """UPDATE leave_requests lr
SET status='approved',
    approved_by={{ $('Merge Data').first().json.emp_id }},
    approved_at=NOW()
FROM employees e
WHERE lr.leave_id={{ $('Merge Data').first().json.leaveId }}
  AND lr.status='pending'
  AND e.emp_id = lr.emp_id
RETURNING lr.leave_id, lr.leave_type, lr.start_date, lr.end_date, lr.total_days,
         e.full_name AS req_name, e.line_user_id AS req_line_id"""

reject_sql = """UPDATE leave_requests lr
SET status='rejected',
    approved_by={{ $('Merge Data').first().json.emp_id }},
    approved_at=NOW(),
    reason = COALESCE(lr.reason,'') || CASE WHEN '{{ $('Merge Data').first().json.leaveReason || '' }}'<>'' THEN E'\\n[ปฏิเสธ] ' || '{{ $('Merge Data').first().json.leaveReason || '' }}' ELSE '' END
FROM employees e
WHERE lr.leave_id={{ $('Merge Data').first().json.leaveId }}
  AND lr.status='pending'
  AND e.emp_id = lr.emp_id
RETURNING lr.leave_id, lr.leave_type, lr.start_date, lr.end_date, lr.total_days,
         e.full_name AS req_name, e.line_user_id AS req_line_id"""

list_pending_sql = """SELECT lr.leave_id, lr.leave_type, lr.start_date, lr.end_date, lr.total_days,
       e.full_name, e.emp_code
FROM leave_requests lr
JOIN employees e ON e.emp_id = lr.emp_id
WHERE lr.status='pending'
ORDER BY lr.created_at DESC LIMIT 10"""

format_list_js = r"""
const rows = $input.all().map(r => r.json);
const replyToken = $('Merge Data').first().json.replyToken;
const typeMap = { sick:'ลาป่วย', annual:'ลาพักร้อน', personal:'ลากิจ', other:'อื่นๆ' };

let msg;
if (rows.length === 0 || !rows[0].leave_id) {
  msg = '✅ ไม่มีใบลารออนุมัติครับ';
} else {
  const lines = rows.map(r => {
    const sd = r.start_date?.toString().slice(0,10) || '';
    const ed = r.end_date?.toString().slice(0,10) || '';
    const range = sd === ed ? sd : `${sd}→${ed}`;
    return `#${r.leave_id} ${r.full_name} • ${typeMap[r.leave_type]||r.leave_type} • ${range} (${r.total_days}วัน)`;
  }).join('\n');
  msg = `📋 ใบลารออนุมัติ ${rows.length} รายการ\n${lines}\n\nคำสั่ง:\n• อนุมัติ <id>\n• ปฏิเสธ <id> [เหตุผล]`;
}
return [{ json: { replyToken, messages: [{ type: 'text', text: msg }] } }];
"""

# Approve admin reply text
approve_admin_text = "={{ $json.leave_id ? '✅ อนุมัติใบลา #' + $json.leave_id + '\\n👤 ' + $json.req_name + '\\nประเภท: ' + $json.leave_type + '\\nวันที่: ' + ($json.start_date+'').slice(0,10) + ' ('+$json.total_days+' วัน)' : '❌ ไม่พบใบลา #' + $('Merge Data').first().json.leaveId + ' หรืออนุมัติ/ปฏิเสธไปแล้ว' }}"

approve_push_text = "={{ '✅ ใบลา #' + $json.leave_id + ' ของคุณได้รับการอนุมัติแล้ว\\nประเภท: ' + $json.leave_type + '\\nวันที่: ' + ($json.start_date+'').slice(0,10) + ' ('+$json.total_days+' วัน)' }}"

reject_admin_text = "={{ $json.leave_id ? '❌ ปฏิเสธใบลา #' + $json.leave_id + '\\n👤 ' + $json.req_name + '\\nประเภท: ' + $json.leave_type : '❌ ไม่พบใบลา #' + $('Merge Data').first().json.leaveId + ' หรืออนุมัติ/ปฏิเสธไปแล้ว' }}"

reject_push_text = "={{ '❌ ใบลา #' + $json.leave_id + ' ของคุณถูกปฏิเสธ\\nประเภท: ' + $json.leave_type + '\\nวันที่: ' + ($json.start_date+'').slice(0,10) + ($('Merge Data').first().json.leaveReason ? '\\nเหตุผล: ' + $('Merge Data').first().json.leaveReason : '') }}"

not_allowed_text = "❌ คำสั่งนี้สำหรับ admin (HR/หัวหน้างาน) เท่านั้น"

new_nodes = [
    pg("List Pending Leaves",     [1300, 1020], list_pending_sql),
    code_node("Format List Pending", [1480, 1020], format_list_js),
    {
        "id": new_id(), "name": "Send List Pending",
        "type": "@aotoki/n8n-nodes-line-messaging.lineMessaging",
        "typeVersion": 1, "position": [1700, 1020],
        "parameters": {
            "operation": "replyMessage",
            "replyToken": "={{ $json.replyToken }}",
            "messages": "={{ $json.messages }}",
        },
        "credentials": {"lineMessagingApi": LINE_CRED},
    },
    pg("Approve Leave",           [1300, 1140], approve_sql),
    line_reply("Reply Approve Admin", [1520, 1140], approve_admin_text),
    line_push("Push Approve Requester", [1740, 1140],
              "={{ $json.req_line_id }}", approve_push_text),
    pg("Reject Leave",            [1300, 1280], reject_sql),
    line_reply("Reply Reject Admin", [1520, 1280], reject_admin_text),
    line_push("Push Reject Requester", [1740, 1280],
              "={{ $json.req_line_id }}", reject_push_text),
    line_reply("Reply Not Allowed", [1300, 1420], not_allowed_text),
]

wf["nodes"].extend(new_nodes)

# ---------- 7. Connections ----------
conns = wf["connections"]

# Route output indices: existing = checkin(0), checkout(1), leave(2), help(3),
# add_employee(4), add_employee_error(5), register(6), check_time(7), check_leave(8)
# new = approve_leave(9), reject_leave(10), list_pending(11), not_allowed(12)
route_main = conns["Route"]["main"]
while len(route_main) < 13:
    route_main.append([])

route_main[9]  = [{"node": "Approve Leave",       "type": "main", "index": 0}]
route_main[10] = [{"node": "Reject Leave",        "type": "main", "index": 0}]
route_main[11] = [{"node": "List Pending Leaves", "type": "main", "index": 0}]
route_main[12] = [{"node": "Reply Not Allowed",   "type": "main", "index": 0}]

conns["Approve Leave"] = {"main": [[
    {"node": "Reply Approve Admin",    "type": "main", "index": 0},
    {"node": "Push Approve Requester", "type": "main", "index": 0},
]]}
conns["Reject Leave"] = {"main": [[
    {"node": "Reply Reject Admin",    "type": "main", "index": 0},
    {"node": "Push Reject Requester", "type": "main", "index": 0},
]]}
conns["List Pending Leaves"] = {"main": [[
    {"node": "Format List Pending", "type": "main", "index": 0}
]]}
conns["Format List Pending"] = {"main": [[
    {"node": "Send List Pending", "type": "main", "index": 0}
]]}

# ---------- 8. PUT (strip non-allowed fields) ----------
allowed = {"name", "nodes", "connections", "settings", "staticData"}
payload = {k: v for k, v in wf.items() if k in allowed}

result = http("PUT", f"/workflows/{WORKFLOW_ID}", payload)
print(f"✅ Updated workflow id={result.get('id')} active={result.get('active')} nodes={len(result.get('nodes',[]))}")
