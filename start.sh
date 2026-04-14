#!/bin/bash
# Railway 智能启动脚本

echo "=== Start Script Debug ==="
echo "RAILWAY_SERVICE_NAME=$RAILWAY_SERVICE_NAME"
echo "RAILWAY_SERVICE_ID=$RAILWAY_SERVICE_ID"
echo "========================="

# 检查是否是 Cron 服务 (efficient-creativity)
if [ "$RAILWAY_SERVICE_ID" = "8a4bf064-947e-4d01-aa80-6ae20b7166e9" ]; then
    echo "Starting as Cron service (efficient-creativity)..."
    . /opt/venv/bin/activate
    python backend/cron_tasks.py fetch-market
else
    echo "Starting as Web service..."
    . /opt/venv/bin/activate
    cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT
fi
