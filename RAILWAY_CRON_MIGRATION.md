# 🚂 Railway 云端定时任务 - 完整配置指南

## ✅ 本地任务已删除

- ❌ `/root/global-insight/backend/news_cron.sh` - 已删除
- ❌ `/tmp/news_cron.sh` - 已删除
- ❌ `/tmp/news_cron.log` - 已删除
- ❌ Crontab 任务 - 已移除

## 📋 Railway Cron 配置

### 1. 登录 Railway
- 网址：https://railway.app/
- 项目：`zestful-education`
- 服务：`efficient-creativity`

### 2. 添加 Cron 任务

**进入 Settings → Cron → Add Cron Job**

添加以下任务：

#### 任务 1: 新闻抓取（每 30 分钟）
```
Name: news-fetcher
Schedule: */30 * * * *
Command: python backend/cron_tasks.py fetch-news
```

#### 任务 2: 市场数据（每 30 分钟）
```
Name: market-fetcher
Schedule: */30 * * * *
Command: python backend/cron_tasks.py fetch-market
```

#### 任务 3: AI 洞察（每 1 小时）
```
Name: ai-insights
Schedule: 0 * * * *
Command: python backend/cron_tasks.py generate-insights
```

#### 任务 4: 知识图谱（每 6 小时）
```
Name: graph-builder
Schedule: 0 */6 * * *
Command: python backend/cron_tasks.py build-graph
```

### 3. 验证环境变量

**Settings → Variables** 确保有以下变量：

| 变量名 | 值 | 状态 |
|--------|-----|------|
| `DATABASE_URL` | `postgresql://neondb_owner:***@ep-raspy-mode-amvgg8he-pooler.c-5.us-east-1.aws.neon.tech/neondb` | ✅ |
| `DASHSCOPE_API_KEY` | `sk-***` | ✅ |

### 4. 部署更新

```bash
cd /root/global-insight
git add -A
git commit -m "Update cron tasks for news fetching"
git push origin main
```

Railway 会自动检测并部署。

## 📊 预期效果

### 每 30 分钟执行：
- ✅ Finnhub 新闻 (~100 条)
- ✅ RSS 新闻 (~100 条)
- ✅ Twitter 新闻 (~50 条)
- ✅ 市场数据 (17 个标的)

### 每小时执行：
- ✅ AI 洞察生成

### 每 6 小时执行：
- ✅ 知识图谱构建

**总计**: ~250 条新闻/30 分钟 = ~12,000 条/天

## 🔍 查看日志

**Railway 控制台**：
1. 进入项目 → Deployments
2. 选择对应的 Cron 运行记录
3. 查看日志输出

**日志示例**：
```
📰 Finnhub API...
  获取到 100 条
  ✅ 插入 50 条

📰 中国新闻网财经...
  获取到 30 条
  ✅ 插入 20 条

🐦 Twitter: @Reuters...
  获取到 20 条
  ✅ 插入 10 条

==================================================
✅ 新闻抓取完成！共插入 213 条
==================================================
```

## 📈 验证数据

**检查 Neon 数据库**：
```sql
-- 最近 1 小时的新闻数量
SELECT source, COUNT(*) as count, MAX(created_at) as latest 
FROM news 
WHERE created_at > NOW() - INTERVAL '1 hour' 
GROUP BY source 
ORDER BY latest DESC;

-- 总新闻数
SELECT COUNT(*) FROM news;

-- 最新新闻时间
SELECT MAX(created_at) FROM news;
```

## ⚠️ 注意事项

1. **首次执行**：配置后等待 30 分钟内会执行第一次
2. **Nitter 稳定性**：部分实例可能不稳定，失败会自动跳过
3. **执行时间**：完整抓取约 60-90 秒
4. **日志保留**：Railway 保留最近 100 行日志

## 🎯 完成检查清单

- [ ] 本地 cron 已删除 ✅
- [ ] Railway Cron 任务已添加
- [ ] 环境变量已验证 ✅
- [ ] 代码已部署
- [ ] 第一次执行成功
- [ ] 数据库有新数据
- [ ] 前端显示正常

## 📞 故障排查

### Cron 没有执行？
1. 检查 Railway 项目是否处于 Active 状态
2. 验证 Cron 表达式是否正确
3. 查看 Deployments 日志是否有错误

### 数据没有更新？
1. 检查 DATABASE_URL 是否正确
2. 查看日志中的数据库连接错误
3. 验证表结构是否存在

### Twitter 抓取失败？
- Nitter 实例可能不稳定，这是正常的
- 其他来源会继续执行
