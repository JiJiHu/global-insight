#!/bin/bash
# Finance Dashboard 定时抓取脚本
# 每 5 分钟执行一次

set -e

BACKEND_DIR="/root/finance-dashboard/backend"
LOG_FILE="/var/log/finance-market.log"

cd "$BACKEND_DIR"
source venv/bin/activate

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始抓取金融数据..." >> "$LOG_FILE"

# 执行抓取（只抓取美股，其他数据源暂不可用）
python fetch_market_data.py >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 抓取完成" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
