#!/usr/bin/env bash
set -euo pipefail

cd /opt/hr-system

echo "=== Docker containers ==="
docker compose ps

echo
echo "=== PostgreSQL tables ==="
docker exec hr_postgres psql -U postgres -d hr_system -c "\dt public.*"

echo
echo "=== n8n logs last 80 lines ==="
docker compose logs --tail=80 n8n
