#!/usr/bin/env bash
# Starts the API, the dashboard and RahulCoolGram together. Ctrl+C stops all three.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

if ! nc -z localhost 5432 2>/dev/null; then
  echo "Postgres is not running on localhost:5432. Start it first (docker compose up -d --wait)."
  exit 1
fi

# Each app gets its own process group, so stopping it also stops its reloader and workers.
set -m
GROUPS_STARTED=()

# Runs a command in an app folder, prefixing each output line with the app name.
start() {
  local name="$1" folder="$2"
  shift 2
  (cd "$ROOT/$folder" && "$@" 2>&1 | sed -u "s/^/[$name] /") &
  GROUPS_STARTED+=("$!")
}

stop_all() {
  trap - INT TERM EXIT
  echo "Stopping..."
  for group in "${GROUPS_STARTED[@]}"; do
    kill -TERM -- "-$group" 2>/dev/null || true
  done
  wait 2>/dev/null || true
}
trap stop_all INT TERM EXIT

start api apps/api uv run fastapi dev
start web apps/web npm run dev
start rahulcoolgram apps/rahulcoolgram uv run fastapi dev --port 8100

echo "API            http://localhost:8000/docs"
echo "Dashboard      http://localhost:3000"
echo "RahulCoolGram  http://localhost:8100"
echo "Ctrl+C stops all three."

wait
