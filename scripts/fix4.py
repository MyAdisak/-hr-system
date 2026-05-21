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

MSG = {
    "Reply Check-in": "={{ '✅ ' + $('Merge Data').first().json.full_name + ' เข้างานแล้วครับ' }}",
    "Reply Check-out": "={{ '👋 ' + $('Merge Data').first().json.full_name + ' ออกงานแล้วครับ' }}",
    "Reply Leave": "บันทึกคำขอลาแล้วครับ",
    "Reply Not Registered": "❌ ยังไม่ได้ลงทะเบียนครับ พิมพ์: ลงทะเบียน EMPxxx",
    "Reply Not Allowed": "❌ คำสั่งนี้สำหรับ admin เท่านั้นครับ",
    "Reply Add Employee": "={{ '✅ เพิ่มพนักงาน ' + $json.full_name + ' (' + $json.emp_code + ') เรียบร้อยครับ' }}",
    "Reply Format Error": "❌ รูปแบบไม่ถูกต้องครับ",
    "Reply Register": "={{ $json.emp_id ? '✅ ลงทะเบียนสำเร็จครับ ' + $json.full_name : '❌ ไม่พบรหัสพนักงานครับ' }}",
    "Reply Check Time": "={{ $json.work_date ? '🕐 เข้า: ' + ($json.check_in || '-') + ' ออก: ' + ($json.check_out || '-') : 'ยังไม่มีข้อมูลวันนี้ครับ' }}",
    "Reply Approve Admin": "={{ '✅ อนุมัติใบลา #' + $json.leave_id + ' เรียบร้อยครับ' }}",
    "Reply Reject Admin": "={{ '❌ ปฏิเสธใบลา #' + $json.leave_id + ' เรียบร้อยครับ' }}",
    "Send Leave Reply": "={{ $json.text || 'ดำเนินการเรียบร้อยครับ' }}",
    "Send List Pending": "={{ $json.text || 'ไม่มีใบลารอครับ' }}",
}

for n in wf["nodes"]:
    name = n["name"]
    if "lineMessaging" not in n.get("type", ""):
        continue
    p = n["parameters"]
    op = p.get("operation", "")
    if op == "replyMessage" and "replyToken" not in p:
        p["replyToken"] = "={{ $('Merge Data').first().json.replyToken }}"
        p["messages"] = [{"type": "text", "text": MSG.get(name, "ดำเนินการเรียบร้อยครับ")}]
        print(f"  fixed: {name}")
    elif op == "pushMessage" and "to" not in p:
        if name == "Push Approve Requester":
            p["to"] = "={{ $json.line_user_id }}"
            p["messages"] = [{"type": "text", "text": "={{ '✅ ใบลา #' + $json.leave_id + ' ได้รับการอนุมัติแล้วครับ' }}"}]
        elif name == "Push Reject Requester":
            p["to"] = "={{ $json.line_user_id }}"
            p["messages"] = [{"type": "text", "text": "={{ '❌ ใบลา #' + $json.leave_id + ' ถูกปฏิเสธครับ' }}"}]
        print(f"  fixed push: {name}")

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
    print(f"PUT error {e.code}: {e.read().decode()}")
