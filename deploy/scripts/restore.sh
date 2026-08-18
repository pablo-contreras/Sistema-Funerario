#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Uso: sudo ./deploy/scripts/restore.sh /mnt/funeraria-backups/AAAA-MM-DD_HH-MM-SS"
  exit 1
fi

PROJECT_DIR="${PROJECT_DIR:-/opt/sistema-funerario}"
BACKUP_PATH="$(realpath "$1")"
cd "$PROJECT_DIR"
set -a
source .env
set +a

test -f "$BACKUP_PATH/base-datos.dump"
sha256sum -c "$BACKUP_PATH/SHA256SUMS"

docker compose exec -T db dropdb --username "$POSTGRES_USER" --if-exists "$POSTGRES_DB"
docker compose exec -T db createdb --username "$POSTGRES_USER" "$POSTGRES_DB"
docker compose exec -T db pg_restore \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --clean --if-exists < "$BACKUP_PATH/base-datos.dump"

if [ -f "$BACKUP_PATH/documentos.tar.gz" ]; then
  tar -C "$DATA_DIR" -xzf "$BACKUP_PATH/documentos.tar.gz"
fi

docker compose restart web
echo "Restauración terminada. Revise el sistema antes de habilitar usuarios."
