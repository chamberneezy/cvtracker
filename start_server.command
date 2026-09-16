#!/bin/bash
cd "$(dirname "$0")"
python3 dev_server.py 8003 &
SERVER_PID=$!
trap "kill $SERVER_PID 2>/dev/null" EXIT INT TERM
sleep 1
open "http://localhost:8003"
echo "Serving http://localhost:8003 (no-cache, auto-reload on file changes) — close this window (or press Ctrl+C) to stop."
wait $SERVER_PID
