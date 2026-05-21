#!/usr/bin/env python3
"""
Fix Merge Data so AI fallback context (action mapped by AI) takes precedence over Parse LINE Event raw output.
"""
import json, os, sys, urllib.request

WORKFLOW_ID = "9kH7p3Hm9dZE3iiG"
N8N_BASE = "http://hr_n8n:5678"

NEW_MERGE_CODE = '''
// Use AI Action Mapper output if AI path was taken, else fall back to Parse LINE Event
let lineData;
try {
  lineData = $('AI Action Mapper').first().json;
} catch (e) {
  lineData = $('Parse LINE Event').first().json;
}
const empRow = $input.first().json;

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
'''.lstrip()

def load_env():
    env={}
    with open(os.environ.get("ENV_FILE","/env")) as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v=line.split("=",1); env[k.strip()]=v.strip().strip('"').strip("'")
    return env

def http(method, url, headers=None, data=None):
    req=urllib.request.Request(url, method=method, headers=headers or {})
    if data is not None: req.data=json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")

def main():
    env=load_env()
    headers={"X-N8N-API-KEY":env["N8N_API_KEY"], "Content-Type":"application/json"}
    code, wf = http("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers)
    if code!=200: sys.exit(f"GET fail {code}")
    print(f"GET ok — {wf['name']}, nodes={len(wf['nodes'])}")
    md = next(n for n in wf["nodes"] if n["name"]=="Merge Data")
    md["parameters"]["jsCode"] = NEW_MERGE_CODE
    print("patched Merge Data jsCode")
    payload={"name":wf["name"],"nodes":wf["nodes"],"connections":wf["connections"],"settings":wf.get("settings",{})}
    code, resp = http("PUT", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers, payload)
    if code!=200: sys.exit(f"PUT fail {code} {resp}")
    print("PUT ok")
    code, after = http("GET", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}", headers)
    if code==200 and not after.get("active"):
        c2,_ = http("POST", f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}/activate", headers, {})
        print(f"reactivated: {c2}")
    print("DONE")

if __name__=="__main__": main()
