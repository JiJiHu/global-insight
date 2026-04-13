#!/bin/bash
# Global Insight 数据更新任务配置

echo "🔧 配置 Global Insight 定时任务..."

# 1. 美股数据 - 每 10 分钟
(crontab -l 2>/dev/null | grep -v "global-insight-backend.*fetch_market_data" || true; \
echo "*/10 * * * * docker exec global-insight-backend python3 /app/fetch_market_data.py >> /var/log/global-insight/market.log 2>&1") | crontab -
echo "   ✅ 美股数据：每 10 分钟"

# 2. 大宗商品数据 - 每 10 分钟
(crontab -l 2>/dev/null | grep -v "global-insight-backend.*fetch_commodities" || true; \
echo "*/10 * * * * docker exec global-insight-backend python3 /app/fetch_commodities.py >> /var/log/global-insight/commodities.log 2>&1") | crontab -
echo "   ✅ 大宗商品数据：每 10 分钟"

# 3. AI 洞察生成 - 每小时
(crontab -l 2>/dev/null | grep -v "global-insight-backend.*generate_insights" || true; \
echo "0 * * * * docker exec global-insight-backend python3 /app/generate_insights_v2.py >> /var/log/global-insight/insights.log 2>&1") | crontab -
echo "   ✅ AI 洞察：每小时"

# 4. 新闻抓取 - 每 30 分钟
(crontab -l 2>/dev/null | grep -v "global-insight-backend.*fetch_news" || true; \
echo "*/30 * * * * docker exec global-insight-backend python3 /app/fetch_news.py >> /var/log/global-insight/news.log 2>&1") | crontab -
echo "   ✅ 新闻数据：每 30 分钟"

echo ""
echo "📋 当前定时任务列表:"
crontab -l | grep global-insight

echo ""
echo "✅ Global Insight 定时任务配置完成！"
