#!/bin/bash
# 知识图谱生成定时任务
# 每 4 小时执行一次

set -e

BACKEND_DIR="/root/finance-dashboard/backend"
LOG_FILE="/var/log/finance-graph.log"

cd "$BACKEND_DIR"
source venv/bin/activate

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始生成知识图谱..." >> "$LOG_FILE"

# 生成图谱
python knowledge_graph.py >> "$LOG_FILE" 2>&1

# 复制图谱数据到容器
docker cp graph_data.json finance-backend:/app/graph_data.json

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 知识图谱生成完成" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
