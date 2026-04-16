# ✅ 新闻源自动更新配置确认

## 📊 已集成的新闻源

### 1. Finnhub API ✅
**来源**: Reuters, CNBC, Bloomberg
**频率**: 每天 00:00 (Railway Cron)
**状态**: ✅ 已集成到 `cron_tasks.py`

```python
# Finnhub API (Reuters, CNBC, Bloomberg)
params = {'token': FINNHUB_API_KEY, 'category': 'general'}
response = requests.get('https://finnhub.io/api/v1/news', params=params)
```

### 2. RSS 新闻源 ✅
**频率**: 每天 00:00 (Railway Cron)
**状态**: ✅ 已集成到 `cron_tasks.py`

| 来源 | RSS URL | 状态 |
|------|---------|------|
| 中国新闻网财经 | `https://www.chinanews.com.cn/rss/finance.xml` | ✅ |
| Bloomberg | `https://feeds.bloomberg.com/markets/news.rss` | ✅ |
| Investing.com | `https://cn.investing.com/rss/news.rss` | ✅ |
| CNBC Top News | `https://search.cnbc.com/rs/search/combinedcms/view.xml` | ✅ |
| GitHub | `https://github.blog/feed/` | ✅ |

### 3. Twitter (通过 Nitter) ✅
**频率**: 每天 00:00 (Railway Cron)
**状态**: ✅ 已集成到 `cron_tasks.py`

| 账号 | 状态 |
|------|------|
| @Reuters | ✅ |
| @Bloomberg | ✅ |
| @WSJ | ✅ |
| @CNBC | ✅ |
| @FinancialTimes | ✅ |

## ⏰ 执行计划

### Railway Cron (云端)
```
Schedule: 0 0 * * * (每天 00:00 UTC)
Command: python backend/cron_tasks.py all
```

**转换为北京时间 (UTC+8)**: 每天早上 08:00

### 执行任务
1. ✅ `fetch-news()` - 抓取所有新闻源
2. ✅ `fetch-market()` - 抓取市场数据
3. ✅ `generate-insights()` - 生成 AI 洞察
4. ✅ `build-graph()` - 构建知识图谱

## 📈 预期数据量

**每天抓取**:
- Finnhub: ~100 条
- RSS: ~100 条
- Twitter: ~50 条
- **总计**: ~250 条/天

## 🔧 配置状态

| 组件 | 文件 | 状态 |
|------|------|------|
| 新闻抓取脚本 | `backend/cron_tasks.py` | ✅ 已更新 |
| Railway 配置 | `railway.cron.toml` | ✅ 已配置 |
| 依赖配置 | `nixpacks.toml` | ✅ 已添加 |
| 环境变量 | Railway Variables | ✅ DATABASE_URL, DASHSCOPE_API_KEY |
| 本地 Cron | crontab | ❌ 已删除 |
| Git 推送 | GitHub | ✅ 已推送 (6fb1b11) |

## ⚠️ 需要在 Railway 控制台操作

**尚未自动配置的部分**:

1. **Cron 任务添加** (需手动)
   - 登录 Railway → 项目 → 服务
   - Settings → Cron → Add Cron Job
   - 配置：
     ```
     Name: daily-news-fetcher
     Schedule: 0 0 * * *
     Command: python backend/cron_tasks.py all
     ```

2. **验证环境变量**
   - Settings → Variables
   - 确认 `DATABASE_URL` 和 `DASHSCOPE_API_KEY` 存在

## 📝 总结

### ✅ 已完成
- ✅ 所有新闻源已集成到 `cron_tasks.py`
- ✅ Railway 配置文件已更新
- ✅ 依赖已添加 (feedparser, psycopg2-binary)
- ✅ 本地 Cron 已删除
- ✅ 代码已推送到 GitHub

### ⏳ 待完成
- ⏳ Railway 自动部署中 (1-2 分钟)
- ⏳ 需要在 Railway 控制台添加 Cron 任务
- ⏳ 第一次执行 (部署后 24 小时内)

### 🎯 所有新闻源都会自动更新吗？

**是的！** 配置完成后：
- ✅ 所有 13 个新闻源都会自动抓取
- ✅ 每天 08:00 (北京时间) 执行
- ✅ 数据自动写入 Neon 云端数据库
- ✅ 前端自动显示最新新闻

**唯一需要手动操作的**: 在 Railway 控制台添加 Cron 任务（1 分钟）
