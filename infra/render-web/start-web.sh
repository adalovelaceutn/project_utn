#!/usr/bin/env bash
set -euo pipefail

export PORT="${PORT:-10000}"

export MONGO_URI="${MONGO_URI:-mongodb://kolb_user:kolb_pass@127.0.0.1:27017}"
export MONGO_DB_NAME="${MONGO_DB_NAME:-kolb_db}"
export MONGO_KOLB_COLLECTION="${MONGO_KOLB_COLLECTION:-kolb_profiles}"
export MONGO_USERS_COLLECTION="${MONGO_USERS_COLLECTION:-users}"

export API_HOST="0.0.0.0"
export API_PORT="8000"

export A2A_HOST="0.0.0.0"
export A2A_PORT="8001"

export MAIN_HOST="0.0.0.0"
export MAIN_PORT="8002"
export PROFILER_A2A_URL="${PROFILER_A2A_URL:-http://127.0.0.1:8001}"
export API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
export MCP_SERVER_URL="${MCP_SERVER_URL:-http://127.0.0.1:8080/mcp}"

mkdir -p /tmp/mongo-data /tmp/mongo-log
mongod --dbpath /tmp/mongo-data --bind_ip 127.0.0.1 --port 27017 --logpath /tmp/mongo-log/mongod.log --fork

envsubst '${PORT}' < /app/infra/render-web/nginx.render.conf.template > /etc/nginx/conf.d/default.conf

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir /app/data &
PID_DATA=$!

python3 -m uvicorn kolb_profile_server.server:asgi_app --host 0.0.0.0 --port 8080 --app-dir /app/mcp_server-kolb/src &
PID_MCP=$!

python3 -m uvicorn kolb_profiler.a2a.server:app --host 0.0.0.0 --port 8001 --app-dir /app/profiler/src &
PID_PROFILER=$!

python3 -m uvicorn kolb_main.server:app --host 0.0.0.0 --port 8002 --app-dir /app/main/src &
PID_MAIN=$!

nginx -g 'daemon off;' &
PID_NGINX=$!

term_handler() {
  kill "$PID_NGINX" "$PID_MAIN" "$PID_PROFILER" "$PID_MCP" "$PID_DATA" || true
  mongod --dbpath /tmp/mongo-data --shutdown || true
}

trap term_handler SIGTERM SIGINT
wait -n "$PID_NGINX" "$PID_MAIN" "$PID_PROFILER" "$PID_MCP" "$PID_DATA"
term_handler
exit 1
