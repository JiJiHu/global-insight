#!/bin/bash
# Global Insight 自动任务脚本
# 配置数据刷新和系统维护定时任务

set -e

echo "🤖 Global Insight 自动任务配置"
echo "================================"
echo ""

# 1. 数据刷新任务
echo "1️⃣ 配置数据刷新任务..."

# 每 10 分钟刷新大宗商品数据
(crontab -l 2>/dev/null | grep -v "fetch_commodities" || true; echo "*/10 * * * * docker exec finance-backend python3 /app/fetch_commodities.py >> /var/log/finance/commodities.log 2>&1") | crontab -
echo "   ✅ 大宗商品数据：每 10 分钟"

# 每 30 分钟刷新 RSS 新闻
(crontab -l 2>/dev/null | grep -v "fetch_rss_news" || true; echo "*/30 * * * * docker exec finance-backend python3 /app/fetch_rss_news.py >> /var/log/finance/rss_news.log 2>&1") | crontab -
echo "   ✅ RSS 新闻：每 30 分钟"

# 每小时生成 AI 洞察
(crontab -l 2>/dev/null | grep -v "generate_insights" || true; echo "0 * * * * docker exec finance-backend python3 /app/generate_insights_v2.py >> /var/log/finance/insights.log 2>&1") | crontab -
echo "   ✅ AI 洞察：每小时"

# 每天 6 点重建知识图谱
(crontab -l 2>/dev/null | grep -v "build_knowledge_graph" || true; echo "0 6 * * * docker exec finance-backend python3 /app/build_knowledge_graph_v2.py >> /var/log/finance/graph.log 2>&1") | crontab -
echo "   ✅ 知识图谱：每天 6:00"

# 2. 系统维护任务
echo ""
echo "2️⃣ 配置系统维护任务..."

# 每天凌晨 3 点重启浏览器（清理僵尸进程）
(crontab -l 2>/dev/null | grep -v "restart_browser" || true; echo "0 3 * * * /root/finance-dashboard/scripts/restart_browser.sh >> /var/log/finance/browser.log 2>&1") | crontab -
echo "   ✅ 浏览器重启：每天 3:00"

# 每天凌晨 4 点清理僵尸进程
(crontab -l 2>/dev/null | grep -v "cleanup_zombies" || true; echo "0 4 * * * /root/finance-dashboard/scripts/cleanup_zombies.sh >> /var/log/finance/cleanup.log 2>&1") | crontab -
echo "   ✅ 清理僵尸进程：每天 4:00"

# 每天早上 7 点发送健康报告
(crontab -l 2>/dev/null | grep -v "health_report" || true; echo "0 7 * * * /root/finance-dashboard/scripts/health_report.sh >> /var/log/finance/health.log 2>&1") | crontab -
echo "   ✅ 健康报告：每天 7:00"

# 3. 创建日志目录
echo ""
echo "3️⃣ 创建日志目录..."
mkdir -p /var/log/finance
chmod 755 /var/log/finance
echo "   ✅ 日志目录：/var/log/finance"

# 4. 显示当前 crontab
echo ""
echo "4️⃣ 当前 crontab 配置:"
echo "----------------------------------------"
crontab -l | grep -E "(finance|Global)" || echo "   (无相关任务)"
echo "----------------------------------------"

# 5. 创建辅助脚本
echo ""
echo "5️⃣ 创建辅助脚本..."

# 浏览器重启脚本
mkdir -p /root/finance-dashboard/scripts
cat > /root/finance-dashboard/scripts/restart_browser.sh << 'EOF'
#!/bin/bash
# 重启浏览器服务，清理僵尸进程
echo "[$(date)] 重启浏览器服务..."

# 停止旧进程
pkill -f "google-chrome.*18800" 2>/dev/null || true
sleep 2

# 启动新进程
nohup google-chrome-stable \
  --remote-debugging-port=18800 \
  --user-data-dir=/root/.openclaw/browser/openclaw/user-data \
  --no-first-run \
  --no-default-browser-check \
  --disable-sync \
  --disable-background-networking \
  --disable-component-update \
  --disable-features=Translate,MediaRouter \
  --disable-session-crashed-bubble \
  --hide-crash-restore-bubble \
  --password-store=basic \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --disable-setuid-sandbox \
  --disable-dev-shm-usage \
  --disable-blink-features=AutomationControlled \
  --noerrdialogs \
  --ozone-platform=headless \
  --ozone-override-screen-size=800,600 \
  --use-angle=swiftshader-webgl \
  about:blank > /tmp/chrome.log 2>&1 &

sleep 3
echo "[$(date)] 浏览器重启完成"
EOF
chmod +x /root/finance-dashboard/scripts/restart_browser.sh
echo "   ✅ restart_browser.sh"

# 清理僵尸进程脚本
cat > /root/finance-dashboard/scripts/cleanup_zombies.sh << 'EOF'
#!/bin/bash
# 清理 Chrome 僵尸进程
echo "[$(date)] 清理僵尸进程..."

# 查找并清理僵尸进程
ps aux | grep "chrome.*defunct" | grep -v grep | awk '{print $2}' | while read pid; do
    # 僵尸进程无法直接 kill，需要清理父进程
    ppid=$(ps -o ppid= -p $pid 2>/dev/null || echo "")
    if [ -n "$ppid" ] && [ "$ppid" != "1" ]; then
        echo "  清理父进程：$ppid"
        kill -9 $ppid 2>/dev/null || true
    fi
done

# 清理超过 24 小时的 Chrome 进程
ps aux | grep "chrome" | grep -v grep | awk '{if ($10 > 86400) print $2}' | while read pid; do
    echo "  清理超时进程：$pid"
    kill -9 $pid 2>/dev/null || true
done

echo "[$(date)] 清理完成"
EOF
chmod +x /root/finance-dashboard/scripts/cleanup_zombies.sh
echo "   ✅ cleanup_zombies.sh"

# 健康报告脚本
cat > /root/finance-dashboard/scripts/health_report.sh << 'EOF'
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
EOF
chmod +x /root/finance-dashboard/scripts/health_report.sh
echo "   ✅ health_report.sh"

# 6. 初始化日志
echo ""
echo "6️⃣ 初始化日志..."
touch /var/log/finance/{commodities,rss_news,insights,graph,browser,cleanup,health}.log
echo "   ✅ 日志文件已创建"

# 7. 显示总结
echo ""
echo "================================"
echo "✅ 自动任务配置完成！"
echo "================================"
echo ""
echo "📋 任务清单:"
echo "  数据刷新:"
echo "    - 大宗商品：每 10 分钟"
echo "    - RSS 新闻：每 30 分钟"
echo "    - AI 洞察：每小时"
echo "    - 知识图谱：每天 6:00"
echo ""
echo "  系统维护:"
echo "    - 浏览器重启：每天 3:00"
echo "    - 清理僵尸进程：每天 4:00"
echo "    - 健康报告：每天 7:00"
echo ""
echo "📝 日志位置:"
echo "  /var/log/finance/"
echo ""
echo "🔧 管理命令:"
echo "  crontab -l          # 查看任务"
echo "  crontab -e          # 编辑任务"
echo "  crontab -r          # 删除所有任务"
echo ""
echo "📊 查看日志:"
echo "  tail -f /var/log/finance/commodities.log"
echo "  tail -f /var/log/finance/rss_news.log"
echo "  tail -f /var/log/finance/insights.log"
echo ""
