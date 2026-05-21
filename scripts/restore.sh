#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /opt/hr-system/backups/hr_backup_YYYYMMDD_HHMMSS.tar.gz"
  exit 1
fi

FILE="$1"
[[ -f "$FILE" ]] || { echo "File not found: $FILE"; exit 1; }

echo "WARNING: This will restore DB + .env + compose + Caddyfile from backup."
echo "         Current files will be overwritten."
read -rp "Type RESTORE to continue: " OK
[[ "$OK" == "RESTORE" ]] || { echo "Cancelled"; exit 1; }

TMP="$(mktemp -d)"
trap "rm -rf $TMP" EXIT
tar -xzf "$FILE" -C "$TMP"

# Restore configs (backup current first)
STAMP=$(date +%Y%m%d-%H%M%S)
[[ -f /opt/hr-system/.env ]]               && cp /opt/hr-system/.env               /opt/hr-system/.env.bak.$STAMP
[[ -f /opt/hr-system/docker-compose.yml ]] && cp /opt/hr-system/docker-compose.yml /opt/hr-system/docker-compose.yml.bak.$STAMP
cp "$TMP/env"                /opt/hr-system/.env
cp "$TMP/docker-compose.yml" /opt/hr-system/docker-compose.yml
[[ -f "$TMP/Caddyfile" ]] && cp "$TMP/Caddyfile" /opt/hr-system/caddy/Caddyfile

# Restore DB
gunzip -c "$TMP/hr_system.sql.gz" | docker exec -i hr_postgres psql -U postgres -d hr_system

echo "Restore done. Run: docker compose up -d --force-recreate"
