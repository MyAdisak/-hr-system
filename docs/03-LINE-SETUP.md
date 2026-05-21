# 📡 LINE Messaging API — Setup Guide

## 1. สร้าง LINE Channel

1. ไปที่ https://developers.line.biz/console
2. Login ด้วย LINE account
3. **Create a new provider**
4. หน้าผู้ให้บริกา → **Create a Messaging API channel**
5. กรอกจิจการชื่ฯ แล้ว Create

## 2. เก็บ Credentials

| รายการ | ที่ไหน |
|-------|-----|
| Channel Secret | Basic settings → Channel secret |
| Channel Access Token | Messaging API → Issue (ช่องล่าง |

## 3. ใส่ด้วย .env

```bash
nano /opt/hr-system/.env
```

แก้บรรทัด:
```ini
LINE_CHANNEL_ACCESS_TOKEN=<paste_token>
LINE_CHANNEL_SECRET=<paste_secret>
```

สาเพื่ฯ reload:
```bash
cd /opt/hr-system && docker compose up -d
```

## 4. ตั้ง Webhook URL

LINE Developers Console → Messaging API:

- Webhook URL: `https://hr.jodbot.com/webhook/line-handler`
- Use webhook: เปิด
✅
- Auto-reply messages: ปิด ❌
- Greeting messages: ตามใช้
- กด Verify เพื่อทดสอบ

## 5. Add LINE Bot เป็นเพื่อน

Messaging API → QR code → ให้พนักงานสแกน

## 6. ตั้ง Credential ใน n8n

1. เข้า https://hr.jodbot.com
2. Settings → Credentials → New
3. ค้น "Line Messaging" แล้วเลือก
4. ใส่ Channel Secret + Channel Access Token
5. Save

## 7. ทดสอบ

in n8n เปิด workflow → Execute workflow → ส่งข้อความเข้า LINE Bot → ดูว่า workflow ถูก trigger

## Community Node

ระบบติดตั้ง `@aotoki/n8n-nodes-line-messaging` ไว้แล้ว:

- **Line Messaging Trigger** — รับข้อความ
- **Line Messaging** — ส่งข้อความ
- **Line Messaging Data** — ดึงข้อมูล
