#!/bin/bash
# 价格告警检查定时任务
# 每 15 分钟执行一次

set -e

BACKEND_DIR="/root/finance-dashboard/backend"
LOG_FILE="/var/log/finance-alerts.log"

cd "$BACKEND_DIR"
source venv/bin/activate

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始检查价格告警..." >> "$LOG_FILE"

# 执行检查
python price_alerts.py >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 价格告警检查完成" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
