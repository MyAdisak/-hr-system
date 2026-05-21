# HR System — Claude Guide

## กฎ
- ตอบภาษาไทย
- คำสั่งทำลายข้อมูล (DROP/DELETE/TRUNCATE) ถามก่อนเสมอ
- อ่าน `MEMORY_N8N_UPDATE.md` ก่อนเริ่มงาน อัปเดตทุกครั้งที่จบ

## VPS
- IP: `72.62.244.233` | SSH: `ssh hr-vps` (key `~/.ssh/hr_vps`)
- Working dir: `/opt/hr-system/`
- Network: `hr-system_hrnet`

## Stack
| Container | Image | Note |
|-----------|-------|------|
| hr_n8n | n8nio/n8n:latest v2.18.4 | :5678 (internal) |
| hr_postgres | postgres:16-alpine | :5432 (internal) |
| hr_caddy | caddy:2-alpine | :80/:443 |
| hr_n8n_mcp | czlonkowski/n8n-mcp | 127.0.0.1:3000 |
| hr_tailscale | tailscale/tailscale | tailnet IP: 100.95.111.125 |

## Credentials
| รายการ | ค่า |
|--------|-----|
| n8n URL | https://hr.jodbot.com |
| n8n Email | i.am.jodlevel@gmail.com |
| n8n Encryption Key | 475636aa3360701c53a3a586cf1930a22002821ca5b486b09fd683dc987f092e |
| DB name | hr_system |
| DB user/pass (app) | n8n_user / j4CZ0AQK54XAQleI5q7jwSEAun8ypXjYovMfWin1 |
| DB user/pass (super) | postgres / j4CZ0AQK54XAQlel5q7jwSEAun8ypXjYovMfWin1 |

```bash
docker exec -it hr_postgres psql -U postgres -d hr_system
```

## Workflows (active)
| ชื่อ | ID |
|------|----|
| HR - LINE Bot Handler | 9kH7p3Hm9dZE3iiG |
| HR AI Agent | oBCVNG70OYdkYU8L |
| HR - Auto Check-in Daily | cron 08:00 |
| HR - Check-in / Check-out | AZQbKHOROyR97Gz5 |
| HR - Leave Request | YrSzA3pzhTPkYfLH |
| HR - Monthly Payroll | rqrDO7AyE3YrAUp4 |

LINE Webhook ใช้อยู่: `https://hr.jodbot.com/webhook/hr-ai-agent`

## Database Schema
- `employees`: emp_id, emp_code, full_name, daily_wage, status, role, line_user_id
- `attendance`: emp_id, work_date, status(normal/absent), check_in, check_out
- `leave_requests`: emp_id, leave_type, start_date, end_date, total_days, status
- `salary_advances`: emp_id, advance_date, amount, note, deduct_period(YYYY-MM), deduct_status
- `overtime`: emp_id, ot_date, amount, note
- `payroll`: emp_id, month, year, work_days, total_amount, status

รอบเงินเดือน: วันที่ 6 → วันที่ 5 เดือนถัดไป
สูตร: `(วันทำงาน × daily_wage) + OT - เบิกล่วงหน้า`

## พนักงาน (emp_id 1-18)
จ๊อด(1,1000) หมวย(2) มัง(3) เขียว(4,500) ทอง(5,550) พี่วิทย์(6) ยู(7) จอ(8,420) เจมีน(9,400) มีน(10,400) ดู(11,400) ลาย(12,400) เย่(13,400) ติน(14,380) โช(15,390) พลู(16,400) พี่นายแมคโคร(17,600) ปัง(18,400)

## AI Agent Rules
- Model: `claude-haiku-4-5-20251001` | Key: `ANTHROPIC_API_KEY` ใน `.env`
- ห้าม JOIN overtime/salary_advances พร้อม attendance → subquery เสมอ
- พ.ศ. → ค.ศ.: ลบ 543 (2569=2026)

## pgAdmin
https://pgadmin.jodbot.com | admin@hr.com / admin123

## MCP
`ssh -fN -L 3000:localhost:3000 hr-vps` → `http://localhost:3000/mcp`

## USER — จ๊อด
- รันก่อน แก้ทีหลัง | "เงียบ"=เช็ค log | "ผิด"=เช็ค DB | "อีกรอบ"=หาสาเหตุใหม่
- ❌ คำถามเยอะ / อธิบายยาว / confirm ทุกขั้น / recap
- ✅ ตอบตรง best path เดียว command พร้อมใช้ ทดสอบจริงเสมอ
