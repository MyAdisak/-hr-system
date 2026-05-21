# HR System Production Pack — n8n + PostgreSQL + Caddy HTTPS

ชุดนี้ออกแบบสำหรับ Hostinger VPS / Ubuntu 22.04 หรือ 24.04
ใช้ Docker Compose รัน:

- Caddy: reverse proxy + HTTPS อัตโนมัติ
- n8n: workflow automation
- PostgreSQL 16: เก็บข้อมูล n8n + HR database

## วิธีใช้แบบเร็ว

```bash
sudo apt update && sudo apt install -y curl git nano openssl
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo mkdir -p /opt/hr-system
sudo cp -r . /opt/hr-system/
cd /opt/hr-system

sudo chmod +x setup.sh scripts/*.sh
sudo ./setup.sh
sudo docker compose up -d
sudo docker compose logs -f
```

## สำคัญ

1. ต้องมีโดเมนหรือ subdomain ชี้ A record มาที่ IP VPS ก่อน เช่น `hr.example.com`
2. เปิด firewall เฉพาะ 22, 80, 443
3. ไม่ต้องเปิด 5678 ออกเน็ต เพราะ Caddy จะ proxy เข้า n8n ภายใน Docker
4. ไฟล์ `.env` จะถูกสร้างโดย `setup.sh` และเก็บรหัสทั้งหมด
5. ห้ามเปลี่ยน `N8N_ENCRYPTION_KEY` หลังเริ่มใช้งานจริง ไม่งั้น credential ใน n8n จะถอดรหัสไม่ได้

## คำสั่งใช้งานบ่อย

```bash
cd /opt/hr-system

docker compose ps
docker compose logs -f n8n
docker compose restart n8n
docker exec -it hr_postgres psql -U postgres -d hr_system
./scripts/backup.sh
```

## ติดตั้ง LINE Community Node

หลัง n8n เปิดได้แล้ว:

Settings → Community Nodes → Install  
Package:

```text
@aotoki/n8n-nodes-line-messaging
```

## Webhook URL สำหรับ LINE

ตัวอย่าง:

```text
https://hr.example.com/webhook/line/hr
```
