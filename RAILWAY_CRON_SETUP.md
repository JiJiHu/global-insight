# Railway Cron 配置指南 - Global Insight

**更新时间**: 2026-04-14 10:20  
**状态**: ⚠️ 需要手动配置

---

## 📋 当前状态

- ✅ Railway CLI 已登录 (Jiajie Hu)
- ✅ 代码已准备就绪 (`backend/cron_tasks.py`)
- ⚠️ Cron 任务需要在 Railway 网页控制台手动配置

---

## 🔧 配置步骤

### 1️⃣ 访问项目页面

打开浏览器访问：
```
https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f
```

### 2️⃣ 进入 Cron 配置

1. 在项目页面，点击左侧 **"Cron"** 标签（或 Settings → Cron）
2. 点击 **"New Cron Job"** 按钮

### 3️⃣ 添加 4 个定时任务

#### 任务 1: 市场数据抓取（每小时）

```
Name: fetch-market
Schedule: 0 * * * *
Command: python backend/cron_tasks.py fetch-market
```

#### 任务 2: 新闻抓取（每 12 小时）

```
Name: fetch-news
Schedule: 0 6,18 * * *
Command: python backend/cron_tasks.py fetch-news
```

#### 任务 3: AI 洞察生成（每天早上 7 点）

```
Name: generate-insights
Schedule: 0 7 * * *
Command: python backend/cron_tasks.py generate-insights
```

#### 任务 4: 知识图谱构建（每天 2 次）

```
Name: build-graph
Schedule: 30 7,19 * * *
Command: python backend/cron_tasks.py build-graph
```

---

## 📊 Cron Schedule 说明

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ 星期 (0-6, 0=周日)
│ │ │ └─── 月份 (1-12)
│ │ └───── 日期 (1-31)
│ └─────── 小时 (0-23)
└───────── 分钟 (0-59)
```

**示例**：
- `0 * * * *` = 每小时 0 分
- `0 6,18 * * *` = 每天 6:00 和 18:00
- `0 7 * * *` = 每天早上 7:00
- `30 7,19 * * *` = 每天 7:30 和 19:30

---

## ✅ 验证配置

### 1. 查看 Cron 日志

在 Railway 控制台：
1. 点击每个 Cron 任务
2. 查看 **"Logs"** 标签
3. 确认任务执行成功

### 2. 检查 API 数据

```bash
# 市场数据
curl https://global-insight-production.up.railway.app/api/v1/market

# 新闻数据
curl https://global-insight-production.up.railway.app/api/v1/news

# AI 洞察
curl https://global-insight-production.up.railway.app/api/v1/insights
```

---

## 📝 任务说明

| 任务 | 频率 | 功能 | 数据来源 |
|------|------|------|---------|
| fetch-market | 每小时 | 抓取股票/加密货币价格 | yfinance, CoinGecko |
| fetch-news | 每 12 小时 | 抓取财经新闻 | RSS, Twitter |
| generate-insights | 每天 7:00 | 生成 AI 市场分析 | DashScope Qwen |
| build-graph | 每天 7:30, 19:30 | 构建知识图谱 | 市场数据 + 新闻 |

---

## 🆘 故障排查

### Cron 不执行？
1. 检查环境变量 `DATABASE_URL` 是否配置
2. 检查 `DASHSCOPE_API_KEY` 是否配置
3. 查看 Cron 日志中的错误信息

### 任务失败？
1. 查看 Railway 日志
2. 检查 API 限流（yfinance, CoinGecko）
3. 确认数据库连接正常

---

##  本地 Cron（当前运行中）

如果 Railway Cron 配置遇到问题，本地 cron 仍然在运行：

```bash
# 查看当前 cron 配置
crontab -l | grep global-insight

# 日志位置
/var/log/global-insight/market.log
/var/log/global-insight/news-sources.log
/var/log/global-insight/ai-insights.log
/var/log/global-insight/graph.log
```

---

**下一步**: 请在 Railway 网页控制台完成 Cron 配置，完成后告诉我！
