#!/bin/sh
set -eu

APP_DIR="/app/backend/app"
BACKEND_DIR="/app/backend"
MAX_RETRIES="${DB_MIGRATION_MAX_RETRIES:-30}"
SLEEP_SECONDS="${DB_MIGRATION_RETRY_INTERVAL_SECONDS:-2}"

cd "$BACKEND_DIR"

retry_count=1
until alembic -c alembic.ini upgrade head; do
  if [ "$retry_count" -ge "$MAX_RETRIES" ]; then
    echo "alembic migration failed after ${retry_count} attempts" >&2
    exit 1
  fi

  echo "waiting for database before migration (attempt ${retry_count}/${MAX_RETRIES})" >&2
  retry_count=$((retry_count + 1))
  sleep "$SLEEP_SECONDS"
done

cd "$APP_DIR"

exec uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}"
