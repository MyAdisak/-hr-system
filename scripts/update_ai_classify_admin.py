#!/usr/bin/env python3
"""Patch AI Classify Intent (Gemma) sub-workflow:
- Expand intent enum with admin actions
- Inject `current_date` into prompt for relative date resolution
- Activate workflow after patch
"""
import json, os, sys, urllib.request, urllib.error

API_KEY = os.environ['N8N_API_KEY']
WF_ID   = '97lD7mqpfOyvuu6u'
BASE    = 'http://hr_n8n:5678/api/v1'

def req(method, path, body=None):
    url = f'{BASE}{path}'
    data = None
    headers = {'X-N8N-API-KEY': API_KEY, 'Accept': 'application/json'}
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')

# 1. Fetch current
s, wf = req('GET', f'/workflows/{WF_ID}')
print(f'[fetch] status={s}, name={wf.get("name")}, active={wf.get("active")}')

# 2. Patch nodes
NEW_PROMPT_TEXT = (
    "You classify Thai HR LINE messages. Output ONLY a single JSON object on one line. "
    "No prose, no markdown, no code fences.\\n"
    "Schema: {\\\"intent\\\": one of [check_in, check_out, leave_request, salary_inquiry, ot_request, register, help, "
    "admin_mark_leave, admin_mark_absent, admin_mark_half_morning, admin_mark_half_afternoon, unknown], "
    "\\\"confidence\\\": 0-1, "
    "\\\"slots\\\": {\\\"emp_name\\\"?: string, \\\"date_start\\\"?: YYYY-MM-DD, \\\"date_end\\\"?: YYYY-MM-DD, "
    "\\\"leave_type\\\"?: one of [sick, annual, personal, other], \\\"reason\\\"?: string, \\\"emp_code\\\"?: string}}\\n\\n"
    "Resolve relative Thai dates using current_date below.\\n"
    "- วันนี้ = current_date\\n"
    "- พรุ่งนี้ = current_date + 1 day\\n"
    "- มะรืน/มะรืนนี้ = current_date + 2 days\\n"
    "- เมื่อวาน/เมื่อวานนี้ = current_date - 1 day\\n"
    "- ถ้าระบุแค่ '12/5' หรือ '12 พ.ค.' ให้ใช้ปีของ current_date (พ.ศ. → ค.ศ. ลบ 543 แต่ในภาษาไทยมักหมายถึงปีปัจจุบัน)\\n\\n"
    "Admin commands (ผู้ส่งเป็นแอดมินแจ้งคนอื่นลา/ขาด/ครึ่งวัน):\\n"
    "- 'พรุ่งนี้จ๊อดลาป่วย' → admin_mark_leave, slots:{emp_name:'จ๊อด', date_start:tomorrow, leave_type:'sick'}\\n"
    "- 'เขียวลาพักร้อน 10-12 พฤษภา' → admin_mark_leave, slots:{emp_name:'เขียว', date_start:'2026-05-10', date_end:'2026-05-12', leave_type:'annual'}\\n"
    "- 'หมวยขาด' → admin_mark_absent, slots:{emp_name:'หมวย', date_start:today}\\n"
    "- 'ทองครึ่งเช้า' → admin_mark_half_morning, slots:{emp_name:'ทอง', date_start:today}\\n"
    "- 'ลายครึ่งบ่ายวันนี้' → admin_mark_half_afternoon, slots:{emp_name:'ลาย', date_start:today}\\n\\n"
    "Employee self-service:\\n"
    "- 'ลาป่วยพรุ่งนี้' → leave_request, slots:{leave_type:'sick', date_start:tomorrow}\\n"
    "- 'เงินเดือน' → salary_inquiry\\n"
    "- 'ลงทะเบียน EMP005' → register, slots:{emp_code:'EMP005'}\\n\\n"
    "If unclear or off-topic, use intent='unknown' with low confidence.\\n"
)

NEW_HTTP_BODY = (
    '={\n'
    '  "contents": [{\n'
    '    "role": "user",\n'
    '    "parts": [{ "text": "' + NEW_PROMPT_TEXT + '"'
    ' + "\\n\\ncurrent_date: " + new Date().toISOString().slice(0,10)'
    ' + "\\nInput: " + JSON.stringify($json.user_msg)'
    ' + "\\n\\nJSON:" }]\n'
    '  }],\n'
    '  "generationConfig": {\n'
    '    "maxOutputTokens": 300,\n'
    '    "temperature": 0.1\n'
    '  }\n'
    '}'
)

for n in wf['nodes']:
    if n['name'] == 'Gemma - Classify':
        n['parameters']['jsonBody'] = NEW_HTTP_BODY
        print(f'[patch] {n["name"]} — jsonBody updated')

# 3. PUT update (n8n PUT only allows: name, nodes, connections, settings, staticData)
update_body = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {'executionOrder': 'v1'})
}
s, body = req('PUT', f'/workflows/{WF_ID}', update_body)
print(f'[update] status={s}')
if s >= 400:
    print('ERROR:', body)
    sys.exit(1)

# 4. Activate
s, body = req('POST', f'/workflows/{WF_ID}/activate')
print(f'[activate] status={s}, active={body.get("active") if isinstance(body,dict) else body}')

# 5. Activate format-thai too
FMT_ID = 'sF2057d0TJUkiTQT'
s, body = req('POST', f'/workflows/{FMT_ID}/activate')
print(f'[activate format] status={s}, active={body.get("active") if isinstance(body,dict) else body}')

print('DONE')
