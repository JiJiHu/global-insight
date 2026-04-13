#!/bin/bash
# 生成系统健康报告
echo "[$(date)] 生成健康报告..."

REPORT_FILE="/var/log/finance/health_$(date +%Y%m%d).md"

cat > $REPORT_FILE << REPORT
# Global Insight 健康报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 系统状态

### Docker 容器
$(docker-compose ps 2>/dev/null || echo "无法获取容器状态")

### 数据状态
$(curl -s http://localhost:11279/api/v1/stats 2>/dev/null | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    print(f'- 股票：{d.get(\"stock_count\",0)}只')
    print(f'- 黄金：{d.get(\"gold_count\",0)}条')
    print(f'- 石油：{d.get(\"oil_count\",0)}条')
    print(f'- 加密货币：{d.get(\"crypto_count\",0)}条')
    print(f'- 新闻：{d.get(\"news_count\",0)}条')
except:
    print('无法获取数据')
" 2>/dev/null || echo "无法获取 API 数据")

### 浏览器状态
$(curl -s http://127.0.0.1:18800/json/version 2>/dev/null | grep -o '"Browser":.*"' || echo "浏览器未运行")

### 僵尸进程
僵尸进程数：$(ps aux | grep "chrome.*defunct" | grep -v grep | wc -l)

## 建议
$(
ZOMBIES=$(ps aux | grep "chrome.*defunct" | grep -v grep | wc -l)
if [ $ZOMBIES -gt 50 ]; then
    echo "⚠️ 僵尸进程过多，建议手动清理"
else
    echo "✅ 系统运行正常"
fi
)

---
*自动生成*
REPORT

echo "[$(date)] 报告已保存到：$REPORT_FILE"
