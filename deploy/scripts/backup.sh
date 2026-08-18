#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/sistema-funerario}"
cd "$PROJECT_DIR"
set -a
source .env
set +a

BACKUP_ROOT="${BACKUP_DIR:-/mnt/funeraria-backups}"
STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
DEST="$BACKUP_ROOT/$STAMP"
mkdir -p "$DEST"

docker compose exec -T db pg_dump \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --format custom > "$DEST/base-datos.dump"

if [ -d "$DATA_DIR/media" ]; then
  tar -C "$DATA_DIR" -czf "$DEST/documentos.tar.gz" media
fi

cp .env "$DEST/configuracion.env"
chmod 600 "$DEST/configuracion.env"
sha256sum "$DEST"/* > "$DEST/SHA256SUMS"

# Conserva 30 días de copias. Ajuste este plazo según el espacio disponible.
find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf -- {} +
echo "Respaldo creado en $DEST"
