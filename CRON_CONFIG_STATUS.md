# Global Insight Cron 配置状态

**更新时间**: 2026-04-14 10:15  
**状态**: ✅ 本地 Cron 正常运行

---

## 📋 当前配置

### 本地 Crontab 任务

| 任务 | Schedule | 脚本 | 状态 |
|------|----------|------|------|
| 市场数据 | `0 * * * *` (每小时) | `fetch_market_data.py` | ✅ 运行中 |
| 新闻数据 | `0 6,18 * * *` (每天 2 次) | `fetch_news_sources.py` | ✅ 运行中 |
| AI 洞察 | `0 7 * * *` (每天 7:00) | `generate_ai_insights_v3.py` | ✅ 运行中 |
| 知识图谱 | `30 7,19 * * *` (每天 2 次) | `build_knowledge_graph_v2.py` | ✅ 运行中 |

### 查看当前配置
```bash
crontab -l | grep global-insight
```

---

## 📊 数据更新频率

| 数据类型 | 频率 | 下次更新 | 日志 |
|----------|------|----------|------|
| 市场数据 | 每小时 | 下一个整点 | `/var/log/global-insight/market.log` |
| 新闻数据 | 每 12 小时 | 今日 18:00 | `/var/log/global-insight/news-sources.log` |
| AI 洞察 | 每天 1 次 | 明日 07:00 | `/var/log/global-insight/ai-insights.log` |
| 知识图谱 | 每天 2 次 | 今日 19:30 | `/var/log/global-insight/graph.log` |

---

## 🔧 查看日志

```bash
# 实时查看市场数据抓取
tail -f /var/log/global-insight/market.log

# 查看最新 AI 洞察生成
tail -f /var/log/global-insight/ai-insights.log

# 查看知识图谱构建
tail -f /var/log/global-insight/graph.log
```

---

## 🚀 Railway Cron 配置（可选）

如果要将 cron 任务迁移到 Railway，需要：

### 1. 访问 Railway 控制台
https://railway.com

### 2. 找到 global-insight 项目
（当前 CLI 链接的是 zestful-education，需要在网页上找到 global-insight）

### 3. 配置 Cron Jobs

在 Railway 控制台点击 "New" → "Cron Job"，添加以下任务：

| 任务名 | Schedule | Command |
|--------|----------|---------|
| fetch-market | `0 * * * *` | `python backend/cron_tasks.py fetch-market` |
| fetch-news | `0 6,18 * * *` | `python backend/cron_tasks.py fetch-news` |
| generate-insights | `0 7 * * *` | `python backend/cron_tasks.py generate-insights` |
| build-graph | `30 7,19 * * *` | `python backend/cron_tasks.py build-graph` |

### 4. 确保环境变量已配置
- `DATABASE_URL` - Railway PostgreSQL 连接字符串
- `DASHSCOPE_API_KEY` - DashScope API 密钥

---

## 📝 当前 Docker 容器状态

```bash
# 查看所有容器
docker ps | grep global-insight

# 重启后端容器
docker restart global-insight-backend

# 查看后端日志
docker logs -f global-insight-backend
```

---

## ✅ 验证 Cron 运行

```bash
# 1. 检查 crontab
crontab -l | grep global-insight

# 2. 检查日志文件
ls -lh /var/log/global-insight/

# 3. 检查 API 数据
curl -s http://localhost:8000/api/v1/market | python3 -m json.tool | head -20
```

---

## 🆘 故障排查

### Cron 不执行？
1. 检查 cron 服务：`systemctl status cron`
2. 查看 cron 日志：`grep CRON /var/log/syslog`
3. 检查脚本权限：`ls -la /root/global-insight/backend/*.py`

### 数据不更新？
1. 检查容器状态：`docker ps | grep global-insight`
2. 查看后端日志：`docker logs global-insight-backend`
3. 手动执行脚本：`docker exec global-insight-backend python3 /app/fetch_market_data.py`

---

**配置完成！** 🎉
