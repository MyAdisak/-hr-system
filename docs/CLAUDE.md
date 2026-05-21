# HR System Control — คู่มือสำหรับ Claude

## กฎสำคัญ

- **ตอบเป็นภาษาไทยเสมอ**
- **ก่อนรันคำสั่งทำลายข้อมูล (DROP, DELETE, rm -rf, truncate ฯลฯ) ต้องถามผู้ใช้ก่อนเสมอ**
- **ทุกครั้งที่ต้องทำงานบน VPS ให้ SSH เข้าเครื่องก่อนแล้วค่อยดำเนินการ**
- **ความจำหลัก**: อ่าน `MEMORY_N8N_UPDATE.md` (root project) หรือ `/opt/hr-system/docs/MEMORY_N8N_UPDATE.md` ก่อนเริ่มงานทุกครั้ง — และ **อัปเดตทุกครั้งที่จบงาน**
- **SSH**: ใช้ alias `ssh hr-vps` (config อยู่ที่ `~/.ssh/config`, key `~/.ssh/hr_vps`) — ไม่ใช้ password

---

## VPS Hostinger

| รายการ | ค่า |
|--------|-----|
| OS | Ubuntu 22.04 |
| IP | 72.62.244.233 |
| SSH User | root |
| SSH Password | Fb,3A/qxl(Z;?PuV |

การ SSH เข้าเครื่อง:
```bash
ssh root@72.62.244.233
# password: Fb,3A/qxl(Z;?PuV
```

---

## ระบบ HR (Docker Compose)

ติดตั้งอยู่ที่: `/opt/hr-system/`

### Services (3 ตัว)

| Service | Container Name | คำอธิบาย |
|---------|---------------|-----------|
| n8n | hr_n8n | Workflow automation / HR engine |
| PostgreSQL | hr_postgres | ฐานข้อมูลหลัก |
| Caddy | hr_caddy | Reverse proxy + HTTPS auto Let's Encrypt |

คำสั่งพื้นฐาน:
```bash
cd /opt/hr-system
docker compose ps
docker compose logs -f
docker compose restart
```

---

## Domains & HTTPS

| Domain | ใช้สำหรับ |
|--------|-----------|
| hr.jodbot.com | n8n editor (หลัก) |
| jodbot.com | Backup |

HTTPS จัดการโดย Caddy อัตโนมัติผ่าน Let's Encrypt

---

## n8n

| รายการ | ค่า |
|--------|-----|
| URL | https://hr.jodbot.com |
| Login Email | i.am.jodlevel@gmail.com |
| Role | Owner |
| Encryption Key | 475636aa3360701c53a3a586cf1930a22002821ca5b486b09fd683dc987f092e |

### Nodes ที่ติดตั้งเพิ่ม
- `@aotoki/n8n-nodes-line-messaging` — LINE Community Node

---

## PostgreSQL

| รายการ | ค่า |
|--------|-----|
| Database | hr_system |
| Application User | n8n_user |
| App Password | j4CZ0AQK54XAQleI5q7jwSEAun8ypXjYovMfWin1 |
| Superuser | postgres |
| Superuser Password | j4CZ0AQK54XAQlel5q7jwSEAun8ypXjYovMfWin1 |

เข้า psql:
```bash
docker exec -it hr_postgres psql -U n8n_user -d hr_system
# หรือ superuser:
docker exec -it hr_postgres psql -U postgres -d hr_system
```

### Schema

| Schema | เนื้อหา |
|--------|---------|
| `public` | HR tables (13 ตาราง) |
| `n8n` | n8n internal tables |

---

## เอกสาร

เก็บที่: `/opt/hr-system/docs/` (มี 6 ไฟล์)

```bash
ls /opt/hr-system/docs/
```

---

## Workflow มาตรฐานเมื่อรับงาน

1. **อ่าน `MEMORY_N8N_UPDATE.md` ก่อนเสมอ**
2. SSH เข้า VPS: `ssh hr-vps`
3. ไปที่ project: `cd /opt/hr-system`
4. ตรวจสถานะ containers: `docker compose ps`
5. ดำเนินการตามที่ผู้ใช้สั่ง
6. ตรวจสอบ logs หากมีปัญหา: `docker compose logs hr_n8n --tail=50`
7. **อัปเดต `MEMORY_N8N_UPDATE.md` ทั้งใน root + `/opt/hr-system/docs/` เมื่อจบงาน**

---

## n8n MCP Server (deployed 2026-04-30)

| รายการ | ค่า |
|--------|-----|
| Container | `hr_n8n_mcp` (czlonkowski/n8n-mcp:latest) |
| Bind | `127.0.0.1:3000` (localhost only) |
| Auth | Bearer token ที่ `MCP_AUTH_TOKEN` (ใน `.env`) |
| Claude config | registered `n8n` (HTTP) ใน `~/.claude.json` user scope |
| Tunnel | `ssh -fN -L 3000:localhost:3000 hr-vps` (ต้องเปิดก่อนใช้งาน) |
| Tools (no API key) | 7 — docs/template/validate |
| Tools (with API key) | ~22 — เพิ่ม workflow CRUD, executions ฯลฯ |

## Hybrid AI

- **เลือก Option C**: ใช้ **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) สำหรับ routine tasks
- **ไม่ติดตั้ง Ollama** (RAM blocker — VPS 3.8 GB เหลือ 2.6 GB)
- Routing: Haiku → intent/format/classify; Sonnet 4.6 → policy reasoning; Opus 4.7 → schema/payroll edge cases

## Agents (.claude/agents/)

- `debugger.md` — วินิจฉัย workflow/container/webhook ปัญหา (no fix without approval)
- `reviewer.md` — gatekeeper ก่อน apply changes ลง production
- `tester.md` — สร้าง test payload + run end-to-end verify
