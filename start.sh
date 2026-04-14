#!/bin/bash
# Railway 智能启动脚本

# 检查是否是 Cron 服务
if [ "$RAILWAY_SERVICE_NAME" = "efficient-creativity" ]; then
    echo "Starting as Cron service..."
    . /opt/venv/bin/activate
    python backend/cron_tasks.py fetch-market
else
    echo "Starting as Web service..."
    . /opt/venv/bin/activate
    cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT
fi
