#!/bin/bash
# 头条新闻抓取定时任务
# 每 4 小时执行一次（只抓 Top News）

set -e

BACKEND_DIR="/root/finance-dashboard/backend"
LOG_FILE="/var/log/finance-top-news.log"

cd "$BACKEND_DIR"
source venv/bin/activate

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始抓取头条新闻..." >> "$LOG_FILE"

# 执行抓取（只抓 Top News）
python fetch_top_news.py >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 头条新闻抓取完成" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
