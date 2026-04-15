# Global Insight 当前 Cron 配置

## 📋 本地 Crontab 配置

当前系统的 crontab 配置如下：

```bash
# Global Insight 市场数据 - 每小时
0 * * * * docker exec global-insight-backend python3 /app/fetch_market_data.py

# 新闻数据 - 每 12 小时 (06:00, 18:00)
0 6,18 * * * docker exec global-insight-backend python3 /app/fetch_news_sources.py

# AI 洞察 - 每天早上 7 点
0 7 * * * docker exec global-insight-backend python3 /app/generate_ai_insights_v3.py

# 知识图谱 - 每天早上 7:30
30 7,19 * * * docker exec global-insight-backend python /app/build_knowledge_graph_v2.py
```

## 📊 当前数据更新频率

| 数据类型 | 频率 | 时间 | 脚本 |
|----------|------|------|------|
| 市场数据 | 每小时 | 整点 | `fetch_market_data.py` |
| 新闻数据 | 每 12 小时 | 06:00, 18:00 | `fetch_news_sources.py` |
| AI 洞察 | 每天 1 次 | 07:00 | `generate_ai_insights_v3.py` |
| 知识图谱 | 每天 2 次 | 07:30, 19:30 | `build_knowledge_graph_v2.py` |

## 🔧 查看当前 Cron

```bash
crontab -l | grep global-insight
```

## 📝 日志位置

```bash
# 市场数据日志
tail -f /var/log/global-insight/market.log

# 新闻日志
tail -f /var/log/global-insight/news-sources.log

# AI 洞察日志
tail -f /var/log/global-insight/ai-insights.log

# 知识图谱日志
tail -f /var/log/global-insight/graph.log
```

## 🚀 Railway Cron 配置（待配置）

如果要将 cron 任务迁移到 Railway，需要在 Railway 控制台配置：

1. 访问：https://railway.com
2. 找到 global-insight 项目
3. 点击 "New" → "Cron Job"
4. 配置以下任务：

### Railway Cron 任务列表

| 任务名 | Schedule | Command |
|--------|----------|---------|
| fetch-market | `0 * * * *` | `python backend/cron_tasks.py fetch-market` |
| fetch-news | `0 6,18 * * *` | `python backend/cron_tasks.py fetch-news` |
| generate-insights | `0 7 * * *` | `python backend/cron_tasks.py generate-insights` |
| build-graph | `30 7,19 * * *` | `python backend/cron_tasks.py build-graph` |

---

**最后更新**: 2026-04-14
**状态**: ✅ 本地 Cron 运行中
