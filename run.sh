#!/bin/sh
set -eu

APP_DIR="/app/backend/app"

cd "$APP_DIR"

exec uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}"
