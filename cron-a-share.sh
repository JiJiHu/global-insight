#!/bin/bash
# A 股数据抓取定时任务
# 每 5 分钟执行一次（交易时间）

set -e

BACKEND_DIR="/root/finance-dashboard/backend"
LOG_FILE="/var/log/finance-a-share.log"

cd "$BACKEND_DIR"
source venv/bin/activate

# 只在交易时间执行（9:30-11:30, 13:00-15:00）
HOUR=$(date +%H)
MINUTE=$(date +%M)

if [[ ($HOUR -ge 9 && $HOUR -lt 12) || ($HOUR -ge 13 && $HOUR -lt 15) ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始抓取 A 股数据..." >> "$LOG_FILE"
    python fetch_a_share_data.py >> "$LOG_FILE" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] A 股数据抓取完成" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 非交易时间，跳过" >> "$LOG_FILE"
fi

echo "---" >> "$LOG_FILE"
