# MEMORY_N8N_UPDATE.md

> ไฟล์ความจำหลักของระบบ HR System Control
> **Update ทุกครั้งที่จบงาน** — ประหยัด token รื้อฟื้น context
> Last verified state: 2026-05-01 18:50 (LINE↔AI integration ✅ Task E complete — 3/3 e2e tests pass)

---

## 1. State ปัจจุบัน (verified)

### VPS — Hostinger 72.62.244.233 (Ubuntu 22.04)
| Resource | Value | Status |
|---|---|---|
| RAM | 3.8 GiB / Swap 0 | ⚠️ ตึงสำหรับ Ollama |
| Disk | 49 GB / ใช้ 12% | ✅ พอเหลือ |
| Working dir | `/opt/hr-system/` | ✅ |

### Docker Stack (5 services, healthy)
- `hr_n8n` — n8nio/n8n:latest, **v2.18.4**
- `hr_postgres` — postgres:16-alpine (healthy)
- `hr_caddy` — caddy:2-alpine (Let's Encrypt auto) — domain `hr.jodbot.com` + `jodbot.com` (ไม่ใช้ `n8n.jodbot.com`)
- `hr_n8n_mcp` — czlonkowski/n8n-mcp:latest (127.0.0.1:3000, healthy)
- `hr_tailscale` — tailscale/tailscale:stable (network_mode: host) — VPS tailnet IP **100.95.111.125**, hostname `hr-vps-mcp`
- Network: `hr-system_hrnet` (bridge) + host (tailscale)

### n8n
- URL: https://hr.jodbot.com
- Auth: Owner account (`i.am.jodlevel@gmail.com`) — Basic Auth deprecated
- Community node: `@aotoki/n8n-nodes-line-messaging` ติดตั้งแล้ว
- Encryption key: `475636aa3360701c53a3a586cf1930a22002821ca5b486b09fd683dc987f092e`

### Workflows ที่ active (4 ตัว) + Sub-workflows AI (2 ตัว)
| ชื่อ | Active | Nodes | สถานะ |
|---|---|---|---|
| HR - LINE Bot Handler | ✅ | **39** (35 + 4 AI fallback) | wired AI 2026-05-01 |
| HR - Check-in / Check-out | ✅ | - | success |
| HR - Leave Request | ✅ | - | success |
| HR - Monthly Payroll | ✅ | - | ยังไม่เคยรัน |
| AI - Classify Intent (Gemma) | sub | **5** (added Build Body) | ID `97lD7mqpfOyvuu6u`, e2e verified 2026-05-01 18:50 |
| AI - Format Thai (Gemma) | sub | **5** (added Build Body) | ID `sF2057d0TJUkiTQT`, schema fix done — ยังไม่ wire เข้า LINE Bot |
- Last execution: 2026-05-01 18:50 (exec 47–49 success, AI fallback verified)
- AI sub-workflows ใช้ `$env.GEMINI_API_KEY` ใน HTTP header `x-goog-api-key` — ต้องการ `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`. Model = `gemma-3-27b-it`
- HTTP body ใช้ `={{ JSON.stringify($json.body) }}` (Build Body code node สร้าง prompt + body object) — **ห้ามใช้ JS concat ภายใน `={ ... }` mode** ทำให้ JSON.parse fail

### Database — PostgreSQL `hr_system`
- 13 tables ใน schema `public`:
  `employees, departments, attendance, leave_requests, payroll, salary_advances, advance_repayments, petty_expenses, petty_expense_items, factory_shipments, shipment_items, admin_notes, chat_sessions`
- Departments seed: ฝ่ายบุคคล / ฝ่ายผลิต / ฝ่ายบัญชี (3 rows)
- **employees: 23 rows** (seeded 2026-04-30 21:35 จาก `ตารางวัน-เวลาทำงานของจ๊อดและหมวย 2569.xlsx`)
- **attendance: 730 rows** (ม.ค. 20, ก.พ. 27, มี.ค. 412, เม.ย. 271)
- **leave_requests: 0 rows** ⚠️

### Schema `employees`
`emp_id, line_user_id, emp_code, full_name, dept_id, position, role, hire_date, base_salary, daily_wage, status, created_at`

### Seeded employees (23, ค่าแรง 1,000 ฿/วัน)
| EMP code | ชื่อ | dept | role |
|---|---|---|---|
| EMP001 | จ๊อด | ฝ่ายบุคคล | admin (หัวหน้างาน) |
| EMP002 | หมวย | ฝ่ายบุคคล | admin (ฝ่ายบุคคล) |
| EMP003-EMP023 | มัง, เขียว, ทอง, พี่วิทย์, ยู, จอ, เจมีน, มีน, ตู, ลาย, เย่, นาย 2, ติน, โช, พลู, พี่นายแมคโคร, ซู, พ่อ, ปัง, เต้อ, เวย์ | ฝ่ายผลิต | employee (พนักงาน) |

### Attendance encoding (ดูจาก Excel cell value)
- `1` → `status='normal'`, `check_in='08:00'`, `check_out='17:00'` (ทำงานเต็มวัน)
- `0.5` → `status='normal'`, `check_in='08:00'`, `check_out='12:00'` (ครึ่งวัน — schema ไม่มี half_day enum, ใช้เวลาเลิกงานบ่งบอก)
- `0` → `status='absent'`, check_in/out NULL
- ว่าง → ไม่ insert

### Payroll formula (รายวัน)
```sql
SELECT
  e.full_name,
  (COUNT(*) FILTER (WHERE a.status='normal' AND a.check_out::time='17:00:00')::numeric
   + 0.5 * COUNT(*) FILTER (WHERE a.status='normal' AND a.check_out::time='12:00:00')) * e.daily_wage AS earned_baht
FROM employees e
LEFT JOIN attendance a ON a.emp_id=e.emp_id
WHERE EXTRACT(MONTH FROM a.work_date) = :month AND EXTRACT(YEAR FROM a.work_date) = :year
GROUP BY e.emp_id, e.full_name, e.daily_wage;
```

---

## 2. งานเสร็จแล้ว ✅

- [x] VPS provisioning + Docker Compose stack
- [x] HTTPS auto (Caddy + Let's Encrypt) ที่ hr.jodbot.com
- [x] PostgreSQL schema HR (13 tables)
- [x] n8n Owner account migration (จาก Basic Auth)
- [x] LINE Messaging community node
- [x] 4 workflows core: LINE Bot, Check-in/out, Leave, Payroll
- [x] Workflow imports จาก local scripts (`scripts/import_workflows.py`)
- [x] LINE webhook ทดสอบได้ (executions success)
- [x] เอกสาร `/opt/hr-system/docs/` (6 ไฟล์)

## 3. งานคงค้าง — Gap ก่อนรองรับ 30 คน ❌

### Critical (ต้องทำก่อน onboard)
- [x] **Seed employees** ✅ 23 คน + 730 attendance records (ม.ค.-เม.ย. 2569)
- [x] **LINE registration workflow** ✅ pattern `ลงทะเบียน EMPxxx` (มีใน LINE Bot Handler มาตั้งแต่แรก, verified 2026-05-01). LINE user_id ยังเป็น NULL ทุกคน → รอจ๊อด/หมวยส่งคำสั่งใน LINE จริง
- [x] **AI fallback (LINE ↔ Gemma)** ✅ 2026-05-01 18:50 — ข้อความที่ไม่ match regex ส่งให้ AI Classify อัตโนมัติ. เพิ่ม 4 nodes (Is Unknown, Prep AI Input, AI Classify, AI Action Mapper). 3/3 e2e tests ผ่าน. Confidence < 0.5 → action='help'. Latency AI path ~1.5-2.5s
- [ ] Attendance edge cases: late, OT, ลืม check-out (half-day handle แล้วผ่าน check_out time)
- [x] **Leave approval flow (single-stage)** ✅ 2026-05-01: `อนุมัติ <id>` / `ปฏิเสธ <id> [เหตุผล]` / `ใบลารอ` (admin only). Push notify ผู้ขอเมื่อ approve/reject. 4 tests ผ่าน
- [x] **Payroll formula verified** ✅ — เอาวันทำงาน × daily_wage. Half-day = 0.5. Sample test มี.ค. 2569: จ๊อด 21,000฿ / หมวย 23,000฿ / เขียว+พี่วิทย์ 26,000฿
- [ ] **AI Format Thai** wire เข้า reply nodes (ปัจจุบันยัง standby — schema fix แล้วแต่ไม่ได้ถูกเรียก)
- [ ] **Admin AI commands** intent: `admin_mark_leave/absent/half_morning/half_afternoon` — AI classify รู้แล้ว แต่ AI Action Mapper map → 'help' (ไม่มี handler ใน Route). ต้องเพิ่ม nodes รับ batch admin commands

### Infrastructure
- [x] **n8n MCP Server** บน VPS — `hr_n8n_mcp` (czlonkowski/n8n-mcp:latest), HTTP mode, port 127.0.0.1:3000, auth token เก็บใน `.env`
- [x] **Claude Code MCP config** — register แล้วใน `~/.claude.json` user scope, status ✓ Connected, **7 tools** (docs mode)
- [x] **Hybrid AI strategy decided**: Option C — ใช้ **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) แทน Ollama (RAM blocker, รักษา stability VPS)
- [x] **n8n API key** — activated 2026-04-30 14:35. JWT key ใส่ใน `.env` `N8N_API_KEY=eyJ...`. MCP tools **24 ตัว** (จาก 7) → workflow CRUD เปิด (`n8n_list_workflows` คืน 4 workflows ถูกต้อง)
- [x] **Tailscale deployed (2026-04-30 21:10)** — `hr_tailscale` ขึ้นแล้ว, VPS IP `100.95.111.125` (hostname `hr-vps-mcp`). Service block อยู่ใน `docker-compose.yml` ตรงก่อน `networks:`. **Tag `tag:server` ถูกตัดออก** — tailnet ACL ของผู้ใช้ยังไม่ define tag นี้ (ถ้าต้องการ tag: ไป define ที่ https://login.tailscale.com/admin/acls ก่อน แล้วสร้าง key ใหม่ + เปิด `--advertise-tags=tag:server`). Laptop `laptop-ihh1kfot` (100.74.56.84) อยู่ใน tailnet เดียวกัน → SSH ผ่าน tailnet ได้: `ssh root@100.95.111.125`
- [x] **Routing Haiku** — workflow templates พร้อม:
  - `.claude/skills/hr-system/templates/ai-classify-intent.json` — sub-workflow รับ `{user_msg, user_id}` → Haiku → return `{intent, confidence, slots}`
  - `.claude/skills/hr-system/templates/ai-format-thai.json` — รับ `{raw_text, tone, max_chars}` → Haiku → return `{formatted}`
  - ใช้ HTTP Request → `https://api.anthropic.com/v1/messages` model `claude-haiku-4-5-20251001`
  - ต้อง n8n credential type **httpHeaderAuth** ชื่อ "Anthropic API Key" (header `x-api-key: <key>`)
  - **ANTHROPIC_API_KEY ใส่แล้ว (2026-04-30 21:10)** ใน `/opt/hr-system/.env` (len=108). **TODO ต่อ**: create n8n credential type `httpHeaderAuth` ชื่อ "Anthropic API Key" (header `x-api-key: ${ANTHROPIC_API_KEY}`) + import 2 workflows (`ai-classify-intent.json`, `ai-format-thai.json`) ผ่าน MCP
- [x] **Backup automation** ✅ 2026-05-01: `/etc/cron.d/hr-backup` daily 02:00, bundle tar.gz (DB + .env + compose + Caddyfile), retention 30 days. Log `/var/log/hr-backup.log`
- [ ] Backup offsite (rsync to S3/Backblaze) — local only ตอนนี้
- [ ] Monitoring (uptime, exec failure alerts)

### Operational
- [ ] Onboarding playbook สำหรับ 30 คน (ทำเป็น batch หรือทยอย?)
- [ ] LINE Rich Menu ตาม role (พนักงาน/หัวหน้า/HR)
- [ ] Audit log สำหรับการแก้ไข payroll
- [ ] Holiday calendar (วันหยุดบริษัท)

---

## 4. n8n MCP Architecture (DEPLOYED ✅)

```
[Claude Code Windows] ──ssh -L 3000──→ [VPS:127.0.0.1:3000]──→ hr_n8n_mcp ──hrnet──→ hr_n8n:5678
```

**Deployed 2026-04-30**:
- Container: `hr_n8n_mcp` (image `ghcr.io/czlonkowski/n8n-mcp:latest`)
- Mode: HTTP, listens `0.0.0.0:3000` ใน container, host bind `127.0.0.1:3000` (localhost only)
- Network: `hr-system_hrnet` — เห็น `hr_n8n:5678` ผ่าน Docker DNS
- Auth: Bearer token ที่ `MCP_AUTH_TOKEN` (.env)
- Health: `curl http://localhost:3000/health` → `{"status":"ok"}`
- Endpoints:
  - `POST /mcp` — JSON-RPC (modern Streamable HTTP)
  - `GET /sse` — SSE legacy
  - `GET /health`

### ขั้นตอน connect จาก Windows (interim, ก่อน Tailscale)
1. เปิด tunnel: `ssh -L 3000:localhost:3000 hr-vps`
2. เพิ่มใน `~/.claude.json` (หรือ `claude mcp add`):
```jsonc
"n8n": {
  "type": "http",
  "url": "http://localhost:3000/mcp",
  "headers": { "Authorization": "Bearer <MCP_AUTH_TOKEN>" }
}
```
3. Restart Claude Code → `/mcp` ตรวจ list

### Tailscale phase 2 (ยังไม่ทำ)
- ติด `tailscale` container บน VPS host network → expose `n8n-mcp` ผ่าน MagicDNS
- ปิด `127.0.0.1:3000:3000` port mapping → ให้ผ่าน tailnet เท่านั้น

---

## 5. Hybrid AI Strategy + RAM Constraint

### ⚠️ RAM Issue
- VPS มีเพียง **3.8 GiB** + swap 0
- Stack ปัจจุบันใช้ ~660 MiB (n8n + postgres + caddy)
- เหลือ available ~2.9 GiB
- Ollama 7B ต้องการ ≥6 GiB → **ใส่ไม่ได้บน VPS ปัจจุบัน**
- Ollama 1.1B (TinyLlama) / 3B (Phi-3-mini) → ใส่ได้แต่คุณภาพต่ำ ไม่คุ้ม

### ทางเลือก (รอผู้ใช้ตัดสินใจ)
1. **อัป VPS เป็น 8 GB plan** (~$15-20/เดือน) → ใช้ Llama 3.1 8B Q4
2. **Ollama บน Windows local** + Tailscale expose → VPS เรียกผ่าน tailnet
3. **เพิ่ม swap 4 GB** (ฟรี แต่ disk thrash, ไม่แนะนำ production)
4. **ใช้ Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) แทน Ollama สำหรับ routine — ถูก ($1/$5 per Mtok), เร็ว, ไม่ต้องดูแล local model

### Routing แผน
| Task type | Engine |
|---|---|
| LINE intent classify (ลา/check-in/ถามเงินเดือน) | Ollama/Haiku — short prompt |
| Format Thai response | Ollama/Haiku |
| Date/time parsing | Ollama/Haiku |
| Payroll dispute resolution | Claude Opus 4.7 |
| HR policy reasoning | Claude Sonnet 4.6 |
| Schema/SQL generation ซับซ้อน | Claude Opus 4.7 |

### Set Node Filter Pattern (ก่อนเข้า Claude)
```
{
  user_msg: $json.message.text,
  intent_hint: $json.detected_intent,
  emp_context: { code: $json.emp_code, dept: $json.dept }
  // ตัด full LINE event payload ทิ้ง
}
```

---

## 6. .claude/agents/ (NEW)

| Agent | Purpose |
|---|---|
| `debugger.md` | วิเคราะห์ workflow execution failure, query logs, ระบุ root cause |
| `reviewer.md` | Review workflow JSON, SQL, .env changes ก่อน apply |
| `tester.md` | สร้าง test payload (LINE webhook, n8n input), run end-to-end |

---

## 7. MCP — Verified end-to-end (2026-04-30 14:16)

```
[Claude Code Windows] ──ssh -L 3000──→ [127.0.0.1:3000 บน VPS] → hr_n8n_mcp → hr_n8n
```

- ทดสอบ `initialize` → 200 OK, session-id ออก
- ทดสอบ `tools/list` → 7 tools (docs mode):
  `tools_documentation, search_nodes, get_node, validate_node, get_template, search_templates, validate_workflow`
- ทดสอบ `tools/call` → `search_nodes("line messaging")` ส่งคืน community node `@aotoki/n8n-nodes-line-messaging.lineMessaging` ถูกต้อง
- เพิ่มเติม management tools (~15 ตัว) จะ available หลัง `N8N_API_KEY` ถูก set

### SSH tunnel persistent
- Manual: `ssh -fN -L 3000:localhost:3000 hr-vps`
- Recommend: ใช้ `autossh` หรือสร้าง Windows Task Scheduler job ที่ login boot

### Claude Code restart
- Tools จาก MCP จะ available **หลัง restart Claude Code** เท่านั้น
- ใน session ปัจจุบัน: `claude mcp list` แสดง connected แต่ไม่เห็น tool ในการแชท จนกว่าจะ restart

## 8. Hybrid AI — Decision: Option C (Haiku)

**Status**: ผู้ใช้เลือก Option C (2026-04-30) — ไม่ติดตั้ง Ollama

### Routing
| Task | Engine | Why |
|---|---|---|
| Intent classify (เข้างาน/ลา/ถาม) | **Haiku 4.5** | ถูก ($1/$5 per Mtok), เร็ว, prompt สั้น |
| Date/time parse Thai | Haiku 4.5 | accuracy พอ, ราคาถูก |
| Format Thai response (Flex Message) | Haiku 4.5 | structured output ทำได้ |
| HR policy reasoning, dispute, complex query | **Sonnet 4.6** | balance |
| Schema migration, payroll edge case | **Opus 4.7** | reasoning ลึก |

### n8n integration plan (TODO)
1. สร้าง credential type "Anthropic API" (n8n built-in มี HTTP Request — ไม่มี Anthropic node native, ใช้ HTTP Request ไปที่ `https://api.anthropic.com/v1/messages`)
2. เก็บ `ANTHROPIC_API_KEY` ใน `.env` + map เข้า n8n env
3. สร้าง subworkflow `AI Classify Intent` ที่รับ text → ส่งไป Haiku → return intent JSON
4. ใน LINE Bot Handler → Set node กรอง payload → call subworkflow → switch ตาม intent

### Set Node filter (ก่อน call AI)
```js
{
  user_msg: $json.events[0].message.text,
  user_id: $json.events[0].source.userId,
  // ตัด full LINE payload ทิ้ง — ส่งแค่ที่จำเป็น
}
```

## 9. Hybrid AI — สถานะ RAM (verified หลัง MCP)

หลังเพิ่ม MCP container (29 MB) สถานะปัจจุบัน:
| Metric | Value |
|---|---|
| Total | 3911 MB |
| Used | 1001 MB |
| Available | **2595 MB** |

| Container | RAM |
|---|---|
| hr_n8n | 629 MB |
| hr_postgres | 34 MB |
| hr_caddy | 21 MB |
| hr_n8n_mcp | 29 MB |

### Ollama feasibility
| Model | RAM ต้องใช้ | ใส่ได้? |
|---|---|---|
| Llama 3.1 8B Q4 | ~5.0 GB | ❌ ไม่ได้ |
| Phi-3-mini 3.8B Q4 | ~2.3 GB | ⚠️ พอดี (เหลือ buffer 295 MB — เสี่ยง OOM) |
| TinyLlama 1.1B Q4 | ~700 MB | ✅ พอ แต่คุณภาพต่ำ |

**สรุป**: VPS plan ปัจจุบัน **ไม่เหมาะรัน Ollama production**. ทางเลือกที่ผู้ใช้ต้องตัดสินใจ:
- (A) อัป VPS เป็น 8 GB → รัน Llama 3.1 8B Q4 ได้สบาย
- (B) Ollama บน Windows local + Tailscale → VPS เรียกผ่าน tailnet
- (C) ใช้ Claude Haiku 4.5 แทน Ollama (recommend — ไม่ต้องดูแล local model)

**ตัดสินใจแล้ว — เลือก Option C (Haiku 4.5)**, **ไม่ติดตั้ง Ollama**

## 10. Quick command reference

| Action | Command |
|---|---|
| SSH | `ssh hr-vps` |
| Status | `ssh hr-vps 'cd /opt/hr-system && docker compose ps'` |
| MCP logs | `ssh hr-vps 'docker logs hr_n8n_mcp --tail=50 -f'` |
| MCP health | `ssh hr-vps 'curl -s localhost:3000/health'` |
| MCP tunnel | `ssh -L 3000:localhost:3000 hr-vps` |
| Backup compose | อัตโนมัติเก็บที่ `/opt/hr-system/docker-compose.yml.bak.YYYYMMDD-HHMM` |
| Restart MCP | `ssh hr-vps 'cd /opt/hr-system && docker compose restart n8n-mcp'` |
| List MCP tools | `claude mcp list \| grep n8n` |
| Open tunnel (Windows bash) | `ssh -fN -L 3000:localhost:3000 hr-vps` |

## 11. Update log

| Date (UTC+7) | Change |
|---|---|
| 2026-04-30 14:04 | สร้างไฟล์, capture state baseline, MCP plan + RAM analysis |
| 2026-04-30 14:07 | Deploy `hr_n8n_mcp` container บน VPS, HTTP mode :3000, healthy. n8n recreated โดย depends_on (no downtime issue) |
| 2026-04-30 14:10 | สร้าง `.claude/agents/{debugger,reviewer,tester}.md` |
| 2026-04-30 14:15 | SSH tunnel `localhost:3000` เปิด, register MCP `n8n` (HTTP + bearer auth) ใน `~/.claude.json` user scope, status ✓ Connected |
| 2026-04-30 14:16 | Verify MCP end-to-end: initialize, tools/list (7 tools), search_nodes("line messaging") return correct community node |
| 2026-04-30 14:18 | ผู้ใช้เลือก Hybrid AI Option C (Haiku 4.5 แทน Ollama). Ollama ไม่ติดตั้ง |
| 2026-04-30 | n8n API key ยังไม่มี (DB `user_api_keys` ว่าง) — รอผู้ใช้ paste key จริง (ครั้งที่แล้วส่ง placeholder text มา) |
| 2026-04-30 14:35 | **n8n API key activated** — JWT ใส่ใน `.env`, recreate `hr_n8n_mcp` (restart ไม่ reload .env). MCP tools 24 ตัว (จาก 7), `n8n_health_check` ผ่าน, `n8n_list_workflows` คืน 4 workflows |
| 2026-04-30 14:42 | **Haiku workflow templates** สร้าง 2 sub-workflows: `ai-classify-intent.json`, `ai-format-thai.json` (ใน `.claude/skills/hr-system/templates/` + `/opt/hr-system/scripts/`). รอ `ANTHROPIC_API_KEY` |
| 2026-04-30 14:43 | **Tailscale prep** — `scripts/tailscale-compose-snippet.yml` พร้อม, state dir สร้าง, `.env` placeholders เพิ่ม. รอ `TS_AUTHKEY` |
| 2026-04-30 21:10 | **Tailscale deployed** — TS_AUTHKEY ใส่แล้ว, append service block (insert ก่อน `networks:`), recreate. Auth fail ครั้งแรกเพราะ `tag:server` ไม่ permitted → ตัด tag ออก. ขึ้น tailnet สำเร็จ IP `100.95.111.125`. **ANTHROPIC_API_KEY ใส่ .env แล้ว** (len=108) — รอ step สร้าง n8n credential + import AI workflows. ผู้ใช้ confirm: ไม่ตั้ง `n8n.jodbot.com` (ใช้ `hr.jodbot.com` ที่มีอยู่), ใช้ `N8N_API_KEY` เดิม. Initial premise ของผู้ใช้ที่ว่า "cloudflared หยุด" ไม่ตรง — ระบบไม่เคยใช้ Cloudflare Tunnel, ใช้ Caddy + Let's Encrypt มาตลอด |
| 2026-04-30 21:14 | **AI integration พร้อม** — เพิ่ม `ANTHROPIC_API_KEY` + `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` ใน n8n compose env, recreate. แก้ template ลบ credential reference, ใช้ `={{ $env.ANTHROPIC_API_KEY }}` ใน HTTP header `x-api-key`. Import 2 sub-workflows ผ่าน n8n Public API (`POST /api/v1/workflows`) — ต้องใช้ `docker run --rm --network=hr-system_hrnet curlimages/curl` เพราะ n8n ไม่ expose port ออก host. **Sanity test Anthropic API**: key valid (HTTP 200) แต่ ❌ **บัญชีหมดเครดิต** — `error: Your credit balance is too low. Please go to Plans & Billing to upgrade`. **Blocker: ผู้ใช้ต้อง top up ที่ https://console.anthropic.com/settings/billing ก่อน Haiku ใช้งานได้** |
| 2026-04-30 21:18 | **Tailscale serve** ลอง enable แต่ tailnet feature ยัง disabled — ต้อง user click `https://login.tailscale.com/f/serve?node=nqsLpMdBZ411CNTRL`. ใช้ SSH tunnel ผ่าน tailnet แทน (`ssh -L 3000:localhost:3000 root@100.95.111.125`) ก็ได้ผลเดียวกัน |
| 2026-04-30 21:35 | **Seed 23 employees + 730 attendance records** จาก Excel `ตารางวัน-เวลาทำงานของจ๊อดและหมวย 2569.xlsx`. Parser script: `scripts/parse_excel_seed.py` → JSON → `scripts/gen_seed_sql.py` → `scripts/seed.sql` (763 lines). จ๊อด=หัวหน้างาน/admin/ฝ่ายบุคคล, หมวย=ฝ่ายบุคคล/admin, ที่เหลือ 21 คน=ฝ่ายผลิต/employee. ค่าแรง 1,000฿/วัน ทุกคน. Attendance encoding: 1→full(08-17), 0.5→half(08-12), 0→absent. Payroll formula verified — มี.ค. 2569: จ๊อด 21,000฿, หมวย 23,000฿. **LINE user_id ยังเป็น NULL ทุกคน** — รอ LINE registration workflow |
| 2026-05-01 05:25 | **Task A — Registration verified working** (ที่จริงมีใน LINE Bot Handler มาตั้งแต่แรก). Pattern `^ลงทะเบียน\s+(\S+)`. Test: webhook → DB UPDATE สำเร็จ. รอจ๊อด/หมวยส่ง `ลงทะเบียน EMP001`/`EMP002` ใน LINE จริง (Anthropic credit ยังหมดอยู่) |
| 2026-05-01 05:40 | **Task B — Backup automation** เสร็จ. แก้ `scripts/backup.sh` ให้ bundle (DB + .env + compose + Caddyfile) เป็น tar.gz ที่ `/opt/hr-system/backups/hr_backup_YYYYMMDD_HHMMSS.tar.gz`. Cron `/etc/cron.d/hr-backup` daily 02:00, retention 30 วัน. แก้ `restore.sh` รองรับ format ใหม่. First backup OK (76 KB). Log: `/var/log/hr-backup.log` |
| 2026-05-01 12:50 | **Task C — Leave approval flow (single-stage)** เสร็จ. ขยาย LINE Bot Handler workflow: 25 → 35 nodes ผ่าน `scripts/add_leave_approval_nodes.py` (Python via docker run python:3.11-alpine ใน hrnet, n8n Public API GET → patch → PUT). คำสั่งใหม่: `อนุมัติ <id>` / `ปฏิเสธ <id> [เหตุผล]` / `ใบลารอ`. Admin guard ใน Merge Data: ถ้า role!=admin + adminOnly action → action='not_allowed'. Push notification ไปยังผู้ขอเมื่อ approve/reject (LINE pushMessage). 4 tests ผ่าน: list_pending, approve, non-admin guard (เขียวลอง approve = no-op), reject with reason. Schema เดิมไม่แตะ — `approved_by`, `approved_at`, `reason` (append `[ปฏิเสธ] ...`) |
| 2026-05-01 13:00 | **Task D — Switch AI Anthropic → Gemini 2.0 Flash (ฟรี)**: เขียน `scripts/switch_ai_to_gemini.py` รอ user paste `GEMINI_API_KEY` จาก aistudio.google.com/apikey. **2 keys ที่ user ลอง: ทั้งคู่ Gemini quota=0** (key แรก: prepayment depleted, key สอง: free tier limit:0). Gemini ถูก lock (อาจเกี่ยว region/account verification). **Workaround: ใช้ Gemma 3 27B IT** ผ่าน same API endpoint (Gemma quota แยก, ใช้งานได้). Constraint Gemma: ไม่รองรับ `responseMimeType` + ไม่รองรับ `system_instruction` → fold prompt เข้า user message + temperature 0.1 + defensive markdown strip ใน Parse node |
| 2026-05-01 13:30 | **Task D — เสร็จ ✅** ผ่าน `scripts/switch_ai_to_gemma.py`. ทั้ง 2 sub-workflows updated: `97lD7mqpfOyvuu6u` → "AI - Classify Intent (Gemma)" + `sF2057d0TJUkiTQT` → "AI - Format Thai (Gemma)". `GEMINI_API_KEY` ใน `.env` (40 chars), `GEMINI_API_KEY=${GEMINI_API_KEY:-}` ใน compose env, recreate n8n. **End-to-end test ผ่าน**: Classify "ลาพักร้อน 10-12 พฤษภา ไปเที่ยวหาดใหญ่" → `{intent:"leave_request",confidence:0.95,slots:{dates,reason}}`. Format Thai "ใบลาถูก reject เพราะลาเยอะไป" → "ขออภัยค่ะ ใบลาของคุณไม่ได้รับการอนุมัติ..." (polite Thai). HTTP node ใช้ `x-goog-api-key: ={{ $env.GEMINI_API_KEY }}` (**หมายเหตุ 2026-05-01 18:50**: test ครั้งนั้นเป็น curl ตรงไป Gemma API ไม่ใช่ผ่าน workflow execution — sub-workflow execution จริง ๆ เพิ่งสำเร็จครั้งแรก 2026-05-01 18:45 หลังแก้ jsonBody bug) |
| 2026-05-01 17:30 | **Task E — Wire AI fallback เข้า LINE Bot Handler**. Script `scripts/wire_ai_into_line_bot.py` — เพิ่ม 4 nodes: `Is Unknown` (IF), `Prep AI Input` (Set), `AI Classify` (executeWorkflow → `97lD7mqpfOyvuu6u`), `AI Action Mapper` (Code: map intent → action + slots, conf<0.5 → help). Workflow 35 → **39 nodes**. แก้ Parse LINE Event: text no-match → push `action='unknown'` (เดิม `continue` ทิ้ง), คง `'skip'` เฉพาะ non-text events. Reviewer agent (`reviewer.md`) ตรวจก่อน apply → catch 3 issues: skip-semantics conflict, `.first()` → `.item`, post-PUT verify active. Backup เดิมเก็บที่ `/opt/hr-system/scripts/line-bot-export.json.bak.beforeai` |
| 2026-05-01 17:50 | **Bug 1 — Gemma jsonBody invalid JSON**. Tester agent (`tester.md`) รัน webhook ทั้ง 5 cases → 2 fail ที่ AI Classify (`Expected ',' or '}' after property value at position 1777`). Root cause: `jsonBody` ใช้ JS concat (`"..." + new Date()... + JSON.stringify(...) + "..."`) ภายใน `={ ... }` expression mode — n8n ไม่ evaluate `+` ภายนอก `{{ }}`. Fix: `scripts/fix_gemma_jsonbody.py` แทรก Code node "Build Body" สร้าง body object → HTTP body = `={{ JSON.stringify($json.body) }}`. ทำทั้ง 2 sub-workflows |
| 2026-05-01 18:30 | **Bug 2 — Merge Data overwrite AI mapping**. หลัง AI Classify success → AI Action Mapper set `action='help', isPublic=true` แต่ flow ยังเข้า Reply Not Registered. Root cause: Merge Data ใช้ `$('Parse LINE Event').first().json` เป็น `lineData` → ดึง action='unknown' กลับมา (เพราะ Parse LINE Event ไม่รู้ว่า AI map แล้ว). Fix: `scripts/fix_merge_data_for_ai.py` — try-catch: ถ้า AI Action Mapper ทำงาน ใช้ output ของมัน, else fallback ไป Parse LINE Event |
| 2026-05-01 18:50 | **Task E — เสร็จ ✅** End-to-end verified 3/3 cases:<br>• rule-match `"เข้า"` → action='checkin', AI **ไม่ถูกเรียก** (regression OK), exec 47<br>• AI register `"ขอลงทะเบียนรหัส EMP005"` → AI intent=register, conf=0.95, action='register', empCode='EMP005', exec 48 → reach **Route**<br>• AI off-topic `"วันนี้อากาศดีจัง"` → AI intent=unknown, conf=0.1, mapper→action='help', exec 45 → reach **Reply Help** ✓<br>**Latency**: rule path 80–180 ms, AI path ~1500–2500 ms (Gemma round-trip dominant). LINE replyToken ปลอม → Reply node อาจ fail ตอน call LINE API จริง แต่ workflow ภายในทำงานครบ |
