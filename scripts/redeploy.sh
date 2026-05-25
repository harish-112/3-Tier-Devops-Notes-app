#!/bin/bash
set -euo pipefail   

docker compose pull

docker compose build --no-cache

echo "==> Reloading Nginx config without restart..."
# Test config is valid BEFORE applying it — never reload a broken config
docker compose exec nginx nginx -t && \
  docker compose exec nginx nginx -s reload

echo "==> Rolling restart: api first, then frontend..."

docker compose up -d --no-deps api
sleep 5
docker compose up -d --no-deps frontend

echo "==> Done. Current status:"
docker compose ps