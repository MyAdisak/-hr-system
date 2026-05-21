# 📚 HR System — Documentation

ระบบ HR ครธวงจร — n8n + PostgreSQL + LINE Chatbot + AI

## 📁 ไฟล์ในเอกสารชุดนี้

| File | Description |
|------|-------------|
| `00-CREDENTIALS.md` | 🔐 รหัสผ่าน + URL ทูกอย่าง |
| `01-SYSTEM-OVERVIEW.md` | 🏗 โครงสร้างระบบ + diagram |
| `02-OPERATIONS.md` | 🛠️ คำสั่งใช้งาน + troubleshooting |
| `03-LINE-SETUP.md` | 📡 ตั้งค่า LINE Bot ที่ละขั้น |
| `04-DATABASE-SCHEMA.md` | 🗔‏ โครงสร้างฐานข้อมูล |

## 🚀 Quick Start

### เข้า n8n
- URL: **https://hr.jodbot.com**
- User: `admin`
- Password: ดูที่ `00-CREDENTIALS.md`

### SSH เข้า VPS
```bash
ssh root@72.62.244.233
```

### ดูสถานะระบบ
```bash
cd /opt/hr-system
docker compose ps
```

## 📋 สิ่งที่ต้องทำต่อ (To-Do)

- [ ] ใส่ `LINE_CHANNEL_ACCESS_TOKEN` ใน `.env`
- [ ] ใส่ `LINE_CHANNEL_SECRET` ใน `.env`
- [ ] ใส่ `OPENAI_API_KEY` ใน `.env`
- [ ] ตั้ง Webhook URL ใน LINE Developers Console
- [ ] Import workflows (ถ้ามีจากเอกสารต้นฉบับ)
- [ ] เพิ่มข้อมูล employees ลง database
- [ ] ทดสอบ workflow แรก
