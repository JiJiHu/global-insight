#!/bin/bash
# AI 洞察生成定时任务
# 每 4 小时执行一次

set -e

BACKEND_DIR="/root/finance-dashboard/backend"
LOG_FILE="/var/log/finance-insights.log"

cd "$BACKEND_DIR"
source venv/bin/activate

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始生成 AI 洞察..." >> "$LOG_FILE"

# 执行生成
python generate_insights.py >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] AI 洞察生成完成" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
