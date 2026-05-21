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
anthropic_key = env["ANTHROPIC_API_KEY"]
line_token = env["LINE_CHANNEL_ACCESS_TOKEN"]
db_pass = env["N8N_DB_PASSWORD"]

headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}

SYSTEM_PROMPT = """คุณคือ HR Assistant AI สำหรับบริษัท ทำงานผ่าน LINE Group ของผู้บริหาร

คุณมีความสามารถ:
1. ดึงข้อมูลพนักงาน การเข้างาน เงินเดือน การลา จาก Database
2. เพิ่ม/แก้ไข/ลบข้อมูล (ต้องขอยืนยันก่อนเสมอ)

Database schema:
- employees: emp_id, emp_code, full_name, dept_id, position, role, hire_date, base_salary, daily_wage, status, line_user_id
- attendance: id, emp_id, work_date, check_in, check_out, status (normal/absent)
- leave_requests: id, emp_id, leave_type, start_date, end_date, total_days, status (pending/approved/rejected), reason
- payroll: id, emp_id, month, year, work_days, total_amount, status

กฎสำคัญ:
- ตอบภาษาไทยเสมอ สุภาพ กระชับ
- ถ้าต้องการ query ข้อมูล ให้ตอบด้วย JSON format: {"action":"query","sql":"SELECT ..."}
- ถ้าต้องการ แก้ไข/เพิ่ม/ลบ ให้ขอยืนยันก่อน: {"action":"confirm","message":"ยืนยันมั้ยครับ? จะ...","sql":"..."}
- ถ้าผู้ใช้พิมพ์ "ยืนยัน" หลังจาก confirm ให้ execute: {"action":"execute","sql":"..."}
- ถ้าแค่ตอบคำถามทั่วไป: {"action":"reply","message":"..."}
- ใช้ emp_code หรือ full_name ในการอ้างอิงพนักงานเสมอ"""

workflow = {
    "name": "HR AI Agent",
    "nodes": [
        {
            "id": "1",
            "name": "LINE Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [200, 300],
            "parameters": {
                "path": "hr-ai-agent",
                "httpMethod": "POST",
                "responseMode": "responseNode"
            }
        },
        {
            "id": "2",
            "name": "Respond OK",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [420, 200],
            "parameters": {
                "respondWith": "text",
                "responseBody": "OK"
            }
        },
        {
            "id": "3",
            "name": "Parse Event",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [420, 380],
            "parameters": {
                "jsCode": """const body = $input.first().json.body;
const event = body.events?.[0];
if (!event || event.type !== 'message' || event.message?.type !== 'text') {
  return [{ json: { skip: true } }];
}
return [{ json: {
  userId: event.source.userId,
  groupId: event.source.groupId || event.source.roomId || null,
  text: event.message.text,
  replyToken: event.replyToken,
  skip: false
}}];"""
            }
        },
        {
            "id": "4",
            "name": "Skip Check",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [640, 380],
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True},
                    "conditions": [{"leftValue": "={{ $json.skip }}", "rightValue": True, "operator": {"type": "boolean", "operation": "equals"}}]
                }
            }
        },
        {
            "id": "5",
            "name": "Load History",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [860, 460],
            "parameters": {
                "jsCode": """// ดึง chat history จาก static data
const userId = $json.userId;
const text = $json.text;
const replyToken = $json.replyToken;

let history = [];
try {
  const stored = $getWorkflowStaticData('global');
  history = stored[userId] || [];
} catch(e) {}

// เก็บแค่ 10 messages ล่าสุด
if (history.length > 10) history = history.slice(-10);

return [{ json: { userId, text, replyToken, history } }];"""
            }
        },
        {
            "id": "6",
            "name": "Call Claude",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1080, 460],
            "parameters": {
                "method": "POST",
                "url": "https://api.anthropic.com/v1/messages",
                "authentication": "none",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "x-api-key", "value": anthropic_key},
                    {"name": "anthropic-version", "value": "2023-06-01"},
                    {"name": "content-type", "value": "application/json"}
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": """={{ JSON.stringify({
  model: "claude-haiku-4-5-20251001",
  max_tokens: 1000,
  system: """ + json.dumps(SYSTEM_PROMPT) + """,
  messages: [...$json.history, {role: "user", content: $json.text}]
}) }}"""
            }
        },
        {
            "id": "7",
            "name": "Parse Claude Response",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1300, 460],
            "parameters": {
                "jsCode": """const response = $json.content?.[0]?.text || '';
const userId = $('Load History').first().json.userId;
const text = $('Load History').first().json.text;
const replyToken = $('Load History').first().json.replyToken;
const history = $('Load History').first().json.history;

// Save to history
const stored = $getWorkflowStaticData('global');
const userHistory = stored[userId] || [];
userHistory.push({role: 'user', content: text});
userHistory.push({role: 'assistant', content: response});
stored[userId] = userHistory.slice(-10);

// Parse JSON action from Claude
let action = 'reply';
let message = response;
let sql = '';

try {
  const jsonMatch = response.match(/\\{[^{}]*"action"[^{}]*\\}/s);
  if (jsonMatch) {
    const parsed = JSON.parse(jsonMatch[0]);
    action = parsed.action || 'reply';
    message = parsed.message || response;
    sql = parsed.sql || '';
  }
} catch(e) {}

return [{ json: { action, message, sql, replyToken, userId } }];"""
            }
        },
        {
            "id": "8",
            "name": "Route Action",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 3,
            "position": [1520, 460],
            "parameters": {
                "mode": "rules",
                "rules": {"values": [
                    {"outputKey": "query", "conditions": {"conditions": [{"leftValue": "={{ $json.action }}", "rightValue": "query", "operator": {"type": "string", "operation": "equals"}}]}},
                    {"outputKey": "execute", "conditions": {"conditions": [{"leftValue": "={{ $json.action }}", "rightValue": "execute", "operator": {"type": "string", "operation": "equals"}}]}},
                ]},
                "fallbackOutput": "extra"
            }
        },
        {
            "id": "9",
            "name": "Run Query",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.5,
            "position": [1740, 360],
            "credentials": {"postgres": {"id": "32vFzlygafyekusC", "name": "HR PostgreSQL"}},
            "parameters": {
                "operation": "executeQuery",
                "query": "={{ $json.sql }}"
            }
        },
        {
            "id": "10",
            "name": "Format Query Result",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1960, 360],
            "parameters": {
                "jsCode": """const rows = $input.all().map(i => i.json);
const replyToken = $('Parse Claude Response').first().json.replyToken;
const userId = $('Parse Claude Response').first().json.userId;
const sql = $('Parse Claude Response').first().json.sql;

// Format result as readable Thai text
let resultText = '';
if (rows.length === 0) {
  resultText = 'ไม่พบข้อมูลครับ';
} else if (rows.length === 1) {
  resultText = Object.entries(rows[0]).map(([k,v]) => k + ': ' + v).join('\\n');
} else {
  resultText = rows.map((r, i) => (i+1) + '. ' + Object.values(r).join(' | ')).join('\\n');
}

// Send back to Claude to format nicely
return [{ json: { replyToken, userId, rawResult: resultText, sql, needsFormat: true } }];"""
            }
        },
        {
            "id": "11",
            "name": "Format With Claude",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [2180, 360],
            "parameters": {
                "method": "POST",
                "url": "https://api.anthropic.com/v1/messages",
                "authentication": "none",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "x-api-key", "value": anthropic_key},
                    {"name": "anthropic-version", "value": "2023-06-01"},
                    {"name": "content-type", "value": "application/json"}
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": """={{ JSON.stringify({
  model: "claude-haiku-4-5-20251001",
  max_tokens: 500,
  messages: [{role: "user", content: "จัดรูปแบบข้อมูลนี้ให้อ่านง่าย เป็นภาษาไทย กระชับ ไม่เกิน 10 บรรทัด:\\n" + $json.rawResult}]
}) }}"""
            }
        },
        {
            "id": "12",
            "name": "Reply Query Result",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [2400, 360],
            "parameters": {
                "method": "POST",
                "url": "https://api.line.me/v2/bot/message/reply",
                "authentication": "none",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "Authorization", "value": f"Bearer {line_token}"},
                    {"name": "Content-Type", "value": "application/json"}
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({replyToken: $('Format Query Result').first().json.replyToken, messages: [{type: 'text', text: $json.content[0].text}]}) }}"
            }
        },
        {
            "id": "13",
            "name": "Execute SQL",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.5,
            "position": [1740, 560],
            "credentials": {"postgres": {"id": "32vFzlygafyekusC", "name": "HR PostgreSQL"}},
            "parameters": {
                "operation": "executeQuery",
                "query": "={{ $json.sql }}"
            }
        },
        {
            "id": "14",
            "name": "Reply Execute Result",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1960, 560],
            "parameters": {
                "method": "POST",
                "url": "https://api.line.me/v2/bot/message/reply",
                "authentication": "none",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "Authorization", "value": f"Bearer {line_token}"},
                    {"name": "Content-Type", "value": "application/json"}
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({replyToken: $json.replyToken, messages: [{type: 'text', text: '✅ ดำเนินการเรียบร้อยแล้วครับ'}]}) }}"
            }
        },
        {
            "id": "15",
            "name": "Reply Message",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1740, 700],
            "parameters": {
                "method": "POST",
                "url": "https://api.line.me/v2/bot/message/reply",
                "authentication": "none",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "Authorization", "value": f"Bearer {line_token}"},
                    {"name": "Content-Type", "value": "application/json"}
                ]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({replyToken: $json.replyToken, messages: [{type: 'text', text: $json.message}]}) }}"
            }
        }
    ],
    "connections": {
        "LINE Webhook": {"main": [[
            {"node": "Respond OK", "type": "main", "index": 0},
            {"node": "Parse Event", "type": "main", "index": 0}
        ]]},
        "Parse Event": {"main": [[{"node": "Skip Check", "type": "main", "index": 0}]]},
        "Skip Check": {"main": [[], [{"node": "Load History", "type": "main", "index": 0}]]},
        "Load History": {"main": [[{"node": "Call Claude", "type": "main", "index": 0}]]},
        "Call Claude": {"main": [[{"node": "Parse Claude Response", "type": "main", "index": 0}]]},
        "Parse Claude Response": {"main": [[{"node": "Route Action", "type": "main", "index": 0}]]},
        "Route Action": {"main": [
            [{"node": "Run Query", "type": "main", "index": 0}],
            [{"node": "Execute SQL", "type": "main", "index": 0}],
            [{"node": "Reply Message", "type": "main", "index": 0}]
        ]},
        "Run Query": {"main": [[{"node": "Format Query Result", "type": "main", "index": 0}]]},
        "Format Query Result": {"main": [[{"node": "Format With Claude", "type": "main", "index": 0}]]},
        "Format With Claude": {"main": [[{"node": "Reply Query Result", "type": "main", "index": 0}]]},
        "Execute SQL": {"main": [[{"node": "Reply Execute Result", "type": "main", "index": 0}]]},
    },
    "settings": {"executionOrder": "v1"}
}

body = json.dumps(workflow).encode()
req = urllib.request.Request(f"{N8N_BASE}/api/v1/workflows", method="POST", headers=headers, data=body)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read())
    wf_id = result['id']
    print(f"Created workflow: {wf_id}")
    
    # Activate
    req2 = urllib.request.Request(f"{N8N_BASE}/api/v1/workflows/{wf_id}/activate", method="POST", headers=headers, data=b'{}')
    with urllib.request.urlopen(req2, timeout=30) as r:
        print("Activated!")
    print(f"Webhook URL: https://hr.jodbot.com/webhook/hr-ai-agent")
except urllib.error.HTTPError as e:
    print(f"Error: {e.read().decode()[:500]}")
