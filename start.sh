#!/bin/bash
set -e

echo "=== Global Insight Startup ==="
echo "Service Type: ${SERVICE_TYPE:-web} (default: web)"

# 激活虚拟环境
if [ -f "/opt/venv/bin/activate" ]; then
    . /opt/venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️ 虚拟环境不存在，使用系统 Python"
fi

# 创建数据库表
echo "📋 创建数据库表..."
python backend/create_tables.py

# 执行任务（默认 web 模式）
if [ "${SERVICE_TYPE}" = "cron" ]; then
    echo "🕐 执行 Cron 任务..."
    python backend/cron_simple.py
else
    echo "🚀 启动 Web 服务..."
    exec uvicorn backend.api:app --host 0.0.0.0 --port ${PORT:-8000}
fi
