#!/bin/bash
# 新闻抓取定时任务
# 每小时执行一次

set -e

BACKEND_DIR="/root/finance-dashboard/backend"
LOG_FILE="/var/log/finance-news.log"

cd "$BACKEND_DIR"
source venv/bin/activate

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始抓取新闻..." >> "$LOG_FILE"

# 执行抓取
python fetch_news.py >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 新闻抓取完成" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
