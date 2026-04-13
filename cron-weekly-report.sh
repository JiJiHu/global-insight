#!/bin/bash
# 周报生成定时任务
# 每周一早上 8 点执行

set -e

BACKEND_DIR="/root/finance-dashboard/backend"
LOG_FILE="/var/log/finance-weekly.log"

cd "$BACKEND_DIR"
source venv/bin/activate

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始生成周报..." >> "$LOG_FILE"

# 生成周报
python generate_weekly_report.py >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 周报生成完成" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
