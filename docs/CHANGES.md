# Updates 2026-04-29

## n8n Authentication Changed
- ❌ Old: Basic Auth (admin / OZdLe09Bsj...) — DEPRECATED in n8n v2.18+
- ✅ New: Owner Account login
  - Email: i.am.jodlevel@gmail.com
  - Password: [SET BY USER — keep in password manager]

## Caddyfile Updated
Added required headers for n8n behind reverse proxy:
- X-Forwarded-Proto https
- Host {host}

## Active Workflows Reset
DB schema was wiped during recovery — old "My workflow", "My workflow 2", "jodbot" workflows are gone.
Fresh start with Personal workspace.
