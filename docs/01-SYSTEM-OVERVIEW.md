# 🏗 HR System — System Overview

## Architecture

```
                    ┌──────────────────────────────────┐
                    │   ผู้ใช้งาน LINE                       │
                    │   - พนักงาน                              │
                    │   - Admin                             │
                    │   - หัวหน้างาน                       │
                    └──────────────────────────────────┘
                                 ผ่าน HTTPS
                                    ▼
                    ┌──────────────────────────────────┐
                    │   LINE Platform                        │
                    │   developers.line.biz                   │
                    └──────────────────────────────────┘
                                    │ Webhook (HTTPS)
                                    ▼
  Hostinger VPS (72.62.244.233) — Ubuntu 22.04

  Caddy (:180, 443)  =�!>  n8n (:5678)  =�!>  PostgreSQL (:5432)
   HTTPS auto            Workflow Engine   n8n schema + HR tables
   Let's Encrypt

                        ▼
                OpenAI API (external)
```

## Stack

| Component | Image | Container | Purpose |
|-----------|-------|-----------|--------|
| Reverse Proxy | `caddy:2-alpine` | `hr_caddy` | HTTPS อัตโนมัติ + reverse proxy |
| Workflow Engine | `n8nio/n8n:latest` | `hr_n8n` | Automation workflows |
| Database | `postgres:16-alpine` | `hr_postgres` | n8n + HR data |

## Domains

| Domain | Status | DNS Type |
|--------|--------|-----------|
| `hr.jodbot.com` | ✅ Active (Direct A record) | A → 72.62.244.233 |
| `jodbot.com` | ✅ Active (Cloudflare proxy) | A → Cloudflare |

## Ports

| Port | Service | Exposed |
|------|---------|---------|
| 22 | SSH | ✅ Public |
| 80 | HTTP (redirects to HTTPS) | ✅ Public |
| 443 | HTTPS | ✅ Public |
| 5432 | PostgreSQL | ❌ Internal Docker only |
| 5678 | n8n | ❌ Internal Docker only |
| `postgres:16-alpine` | `hr_postgres` | n8n + HR data |

## Domains

| Domain | Status | DNS Type |
|--------|--------|-----------|
| `hr.jodbot.com` | ✅ Active (Direct A record) | A → 72.62.244.233 |
| `jodbot.com` | ✅ Active (Cloudflare proxy) | A → Cloudflare |

## Ports

| Port | Service | Exposed |
|------|---------|---------|
| 22 | SSH | ✅ Public |
| 80 | HTTP (redirects to HTTPS) | ✅ Public |
| 443 | HTTPS | ✅ Public |
| 5432 | PostgreSQL | ❌ Internal Docker only |
| 5678 | n8n | ❌ Internal Docker only |
