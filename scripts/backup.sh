#!/usr/bin/env bash
set -euo pipefail

cd /opt/hr-system

DATE="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="/opt/hr-system/backups"
TMP_DIR="$(mktemp -d)"
trap "rm -rf $TMP_DIR" EXIT

mkdir -p "$BACKUP_DIR"

# 1. PostgreSQL dump (workflows + credentials + HR data — all in DB)
docker exec hr_postgres pg_dump -U postgres -d hr_system | gzip > "$TMP_DIR/hr_system.sql.gz"

# 2. Config files (.env has encryption key — restoring without it = lost credentials)
cp /opt/hr-system/.env                    "$TMP_DIR/env"
cp /opt/hr-system/docker-compose.yml      "$TMP_DIR/docker-compose.yml"
cp /opt/hr-system/caddy/Caddyfile         "$TMP_DIR/Caddyfile" 2>/dev/null || true

# 3. Bundle
tar -czf "$BACKUP_DIR/hr_backup_$DATE.tar.gz" -C "$TMP_DIR" .
chmod 600 "$BACKUP_DIR/hr_backup_$DATE.tar.gz"

# 4. Retention: keep 30 days
find "$BACKUP_DIR" -name "hr_backup_*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "hr_system_*.sql.gz" -mtime +30 -delete

SIZE=$(du -h "$BACKUP_DIR/hr_backup_$DATE.tar.gz" | cut -f1)
echo "[$(date "+%F %T")] Backup OK: hr_backup_$DATE.tar.gz ($SIZE)"
