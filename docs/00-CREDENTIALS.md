# 🔐 HR System — Credentials Vault

> **สำคัญ:**  เก็บไฟล์นี้ไว้ในที่ปลอดภัย (Bitwarden / 1Password) — ห้ามแชร์ผ่าน LINE หรืร Email

Generated: 2026-04-29
VPS: Hostinger KVM1 (Malaysia - Kuala Lumpur)

---

## 🌐 URL การเข้าถึ�

| รายการ | URL |
|-------|-----|
| n8n Editor (Production) | https://hr.jodbot.com |
| n8n Editor (Backup) | https://jodbot.com |
| LINE Webhook URL | https://hr.jodbot.com/webhook/... |
| VPS IP | 72.62.244.233 |
| SSH | `ssh root@72.62.244.233` |

---

## 🖵️ VPS / SSH

| รายการ | ค่า |
|--------|-----|
| User | `root` |
| Password | `Fb,3A/qxl(Z;?PuV` |
| Port | 22 |
| OS | Ubuntu 22.04 LTS |

---

## 🐘 PostgreSQL 16

### Superuser

| รายการ | ค่า |
|-------|-----|
| Host | `postgres` ภายใน Docker |
| Port | 5432 (internal เท่านั้น) |
| User | `postgres` |
| Password | `j4CZ0AQK54XAQlel5q7jwSEAun8ypXjYovMfWin1` |
| Database | `hr_system` |

### App User (สำหรับ n8n)

| รายการ | ค่า |
|-------|-----|
| User | `n8n_user` |
| Password | `j4CZ0AQK54XAQleI5q7jwSEAun8ypXjYovMfWin1` |
| Schema (n8n internal) | `n8n` |
| Schema (HR data) | `public` |

### เข้า Postgres
```bash
docker exec -it hr_postgres psql -U postgres -d hr_system
```

---

## 🔧 n8n

| รายการ | ค่า |
|-------|-----|
| Web URL | https://hr.jodbot.com |
| Basic Auth User | `admin` |
| Basic Auth Password | `OZdLe09BsjkKkLyZR5vM58mpRO4dFz0VBUigplES` |
| Encryption Key | `475636aa3360701c53a3a586cf1930a22002821ca5b486b09fd683dc987f092e` |
| Container | `hr_n8n` |
| Internal Port | 5678 |

> ⚠️ **ห้ามเปลี่ยน `N8N_ENCRYPTION_KEY` หลัง deploy** — credentials ใน n8n จะถอดรหัสไม่ได้

---

## 📡 LINE Messaging API

| รายการ | ค่า |
|-------|-----|
| Channel Access Token | ยังไม่ได้ตั้ง เราผ่าน LINE Developers |
| Channel Secret | ยังไม่ได้ตั้ง |
| Webhook URL | https://hr.jodbot.com/webhook/<workflow-path> |

วิธ: แก้ไข `/opt/hr-system/.env` แล้ว `docker compose up -d`

---

## 🤖 OpenAI

| รายการ | ค่า |
|-------|-----|
| API Key | ยังไม่ได้ตั้ง |
| Recommended Model | `gpt-4o-mini` (ประหยัด) หรืร `gpt-4o` |

---

## 📠 ACME / Let's Encrypt

| รายการ | ค่า |
|-------|-----|
| Email | `i.am.jodlevel@gmail.com` |
| Provider | Let's Encrypt (อัตโนมัติผ่าน Caddy) |


---

## 🖡️ LINE Messaging API

| รายการ | ค่า |
|-------|-----|
| Channel Access Token | ยังไม่ได้ตั้ง เราผ่าน LINE Developers |
| Channel Secret | ยังไม่ได้ตั้ง |
| Webhook URL | https://hr.jodbot.com/webhook/<workflow-path> |

ວิธ: แก้ไข `/opt/hr-system/.env` แล้ว `docker compose up -d`

---

## 🤖 OpenAI

| รายการ | ค่า |
|-------|-----|
| API Key | ยังไม่ได้ตั้ง |
| Recommended Model | `gpt-4o-mini` (ประหยัด) หรืฯ `gpt-4o` |

---

## 📠 ACME / Let's Encrypt

| รายการ | ค่า |
|-------|-----|
| Email | `i.am.jodlevel@gmail.com` |
| Provider | Let's Encrypt (อัตโนมัติผ่าน Caddy) |
