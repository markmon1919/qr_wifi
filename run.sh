#!/bin/bash

set -e

echo "=============================="
echo "   STARTING ISP V6 SYSTEM"
echo "=============================="

# --------------------------
# START REDIS (Mongo is using brew service)
# --------------------------

echo "[1/5] Starting MongoDB + Redis..."
docker compose up -d

echo "Waiting for databases..."
sleep 5

# --------------------------
# INITIALIZE MONGODB
# --------------------------

echo "[2/5] Initializing MongoDB..."
python db/db_init.py

# --------------------------
# START API
# --------------------------

echo "[3/5] Starting API..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# --------------------------
# START ENGINE
# --------------------------

echo "[4/5] Starting Consumption Engine..."
python -c "from api.engine import run_engine; run_engine()" &
ENGINE_PID=$!

# --------------------------
# START PORTAL
# --------------------------

echo "[5/5] Starting Portal..."
python portal/app.py &
PORTAL_PID=$!

echo ""
echo "=============================="
echo "      ISP V6 ONLINE"
echo "=============================="
echo "API PID      : $API_PID"
echo "ENGINE PID   : $ENGINE_PID"
echo "PORTAL PID   : $PORTAL_PID"
echo ""

LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "localhost")

echo "API Docs     : http://$LOCAL_IP:8000/docs"
echo "API          : http://$LOCAL_IP:8000"
echo "Portal       : http://$LOCAL_IP:3000"
echo ""

cleanup() {
    echo ""
    echo "Stopping ISP V6..."

    ```
    kill $API_PID 2>/dev/null || true
    kill $ENGINE_PID 2>/dev/null || true
    kill $PORTAL_PID 2>/dev/null || true

    echo "Stopped."
    ```
}

trap cleanup SIGINT SIGTERM

wait
