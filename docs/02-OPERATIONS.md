# 🛠️ HR System — Operations Manual

## คำสั่งใช้งานทั่วไป‏

```bash
cd /opt/hr-system

docker compose ps
docker compose logs -f n8n
docker compose logs -f caddy
docker compose logs -f postgres

docker compose restart n8n
docker compose restart caddy

docker compose restart
docker compose stop
docker compose up -d

docker stats --no-stream
```

## เข้า Database

```bash
docker exec -it hr_postgres psql -U postgres -d hr_system

docker exec hr_postgres psql -U postgres -d hr_system -c "SELECT * FROM employees LIMIT 5;"

docker exec hr_postgres psql -U postgres -d hr_system -c "\\dt public.*"

docker exec hr_postgres psql -U postgres -d hr_system -c "\\dt n8n.*"
```

## Backup

```bash
/opt/hr-system/scripts/backup.sh

docker exec hr_postgres pg_dump -U postgres hr_system > /opt/hr-system/backups/hr_$(date +%Y%m%d_%H%M%S).sql

tar -czf /opt/hr-system/backups/n8n_$(date +%Y%m%d_%H%M%S).tgz -C /opt/hr-system/n8n data
```

## Restore

```bash
/opt/hr-system/scripts/restore.sh /path/to/backup.sql
```

## Health Check

```bash
/opt/hr-system/scripts/healthcheck.sh

curl -sk -o /dev/null -w "n8n HTTPS: %{http_code}\n" https://hr.jodbot.com/
docker compose ps
```

## อัปเดต n8n เป็นเวอร์ชั่นใหม่

```bash
cd /opt/hr-system
docker compose pull n8n
docker compose up -d n8n
docker compose logs -f n8n
```

## ดู / แก้ Caddyfile

```bash
nano /opt/hr-system/caddy/Caddyfile
docker compose restart caddy
```

## ดู / แก้ .env

```bash
nano /opt/hr-system/.env
docker compose up -d
```

## Troubleshooting

### n8n เข้าไม่ได้

```bash
docker logs hr_n8n --tail 50
docker compose restart n8n
```

### SSL ไม่ขึ้น

```bash
docker logs hr_caddy --tail 50
dig +short hr.jodbot.com
```

### Database connection error

```bash
docker logs hr_postgres --tail 30
docker exec hr_postgres pg_isready -U postgres
```

### Disk เต็ม

```bash
df -h
docker system df
docker system prune -a
```
h
docker logs hr_caddy --tail 50
dig +short hr.jodbot.com
```

### Database connection error

```bash
docker logs hr_postgres --tail 30
docker exec hr_postgres pg_isready -U postgres
```

### Disk เต็ม

```bash
df -h
docker system df
docker system prune -a
```
