#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT_DIR"

BACKEND_PORT=8000
FRONTEND_PORT=8001

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

if [ ! -f ".venv/bin/activate" ]; then
  echo "Virtual environment setup is missing."
  exit 1
fi

source .venv/bin/activate
pip install -r requirements.txt

check_backend() {
  python3 - <<'PY' >/dev/null 2>&1
import http.client, json
try:
    conn = http.client.HTTPConnection('127.0.0.1', $BACKEND_PORT, timeout=1)
    conn.request('GET', '/dishes', headers={'Host': '127.0.0.1'})
    res = conn.getresponse()
    body = res.read().decode('utf-8', 'replace')
    if res.status == 200:
        data = json.loads(body)
        if isinstance(data, list):
            raise SystemExit(0)
    raise SystemExit(2)
except ConnectionRefusedError:
    raise SystemExit(1)
except Exception:
    raise SystemExit(2)
PY
}

start_frontend() {
  python3 - <<'PY' >/dev/null 2>&1
import socket
try:
    with socket.create_connection(('127.0.0.1', $FRONTEND_PORT), timeout=1):
        raise SystemExit(0)
except Exception:
    raise SystemExit(1)
PY
}

backend_pid=""
frontend_pid=""

if check_backend; then
  echo "Backend already running at http://127.0.0.1:$BACKEND_PORT"
else
  echo "Starting backend at http://127.0.0.1:$BACKEND_PORT"
  uvicorn backend.app:app --host 127.0.0.1 --port "$BACKEND_PORT" &
  backend_pid=$!
fi

if start_frontend; then
  echo "Frontend already running at http://127.0.0.1:$FRONTEND_PORT"
else
  echo "Starting frontend at http://127.0.0.1:$FRONTEND_PORT"
  python3 -m http.server "$FRONTEND_PORT" --bind 127.0.0.1 --directory frontend &
  frontend_pid=$!
fi

cleanup() {
  echo "Shutting down services..."
  if [ -n "$backend_pid" ]; then
    kill "$backend_pid" 2>/dev/null || true
    wait "$backend_pid" 2>/dev/null || true
  fi
  if [ -n "$frontend_pid" ]; then
    kill "$frontend_pid" 2>/dev/null || true
    wait "$frontend_pid" 2>/dev/null || true
  fi
}

# Trap INT/TERM to perform graceful shutdown of child processes only
trap 'cleanup; exit 0' INT TERM

echo "Backend: http://127.0.0.1:$BACKEND_PORT"
echo "Frontend: http://127.0.0.1:$FRONTEND_PORT"

# Wait for frontend to respond, then open default browser
echo "Waiting for frontend to become ready..."
for i in $(seq 1 20); do
  if python3 - <<PY >/dev/null 2>&1
import http.client
try:
    conn = http.client.HTTPConnection('127.0.0.1', $FRONTEND_PORT, timeout=1)
    conn.request('GET', '/')
    res = conn.getresponse()
    if res.status == 200:
        raise SystemExit(0)
    else:
        raise SystemExit(1)
except Exception:
    raise SystemExit(1)
PY
  then
    echo "Frontend ready."
    # open browser (xdg-open for Linux, fallback to other common tools)
    if command -v xdg-open >/dev/null 2>&1; then
      xdg-open "http://127.0.0.1:$FRONTEND_PORT" >/dev/null 2>&1 || true
    elif command -v gnome-open >/dev/null 2>&1; then
      gnome-open "http://127.0.0.1:$FRONTEND_PORT" >/dev/null 2>&1 || true
    elif command -v open >/dev/null 2>&1; then
      open "http://127.0.0.1:$FRONTEND_PORT" >/dev/null 2>&1 || true
    fi
    break
  fi
  sleep 0.5
done

echo "Press Ctrl+C to stop."

# Wait for children PIDs if any, otherwise block until signal
if [ -n "$backend_pid" ] || [ -n "$frontend_pid" ]; then
  wait
else
  # no child processes started, sleep until interrupted
  while true; do sleep 3600; done
fi
