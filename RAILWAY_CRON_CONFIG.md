# Railway Cron 定时任务配置指南

## ✅ 已部署代码

- ✅ `backend/cron_tasks.py` - 定时任务脚本
- ✅ 已推送到 GitHub

---

## 📋 Railway Cron 配置步骤

### 1️⃣ 打开 Railway 控制台

访问：https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/fee2b7f1-a3e5-4383-a7d2-c633fd4c83e9

### 2️⃣ 进入 Cron 配置

1. 点击 **"Cron"** 标签（或 Settings → Cron）
2. 点击 **"New Cron"** 按钮

### 3️⃣ 添加 4 个定时任务

#### 任务 1: 市场数据抓取（每 10 分钟）

```
Name: fetch-market
Schedule: */10 * * * *
Command: python backend/cron_tasks.py fetch-market
```

#### 任务 2: 新闻抓取（每小时）

```
Name: fetch-news
Schedule: 0 * * * *
Command: python backend/cron_tasks.py fetch-news
```

#### 任务 3: AI 洞察生成（每天 9 点）

```
Name: generate-insights
Schedule: 0 9 * * *
Command: python backend/cron_tasks.py generate-insights
```

#### 任务 4: 知识图谱构建（每天 10 点）

```
Name: build-graph
Schedule: 0 10 * * *
Command: python backend/cron_tasks.py build-graph
```

---

## 🔧 Cron Schedule 说明

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
- `*/10 * * * *` = 每 10 分钟
- `0 * * * *` = 每小时 0 分
- `0 9 * * *` = 每天 9:00
- `0 10 * * *` = 每天 10:00

---

## ✅ 验证配置

### 1. 查看 Cron 日志

在 Railway 控制台：
- 点击每个 Cron 任务
- 查看 **"Logs"** 标签
- 确认任务执行成功

### 2. 检查数据库

```bash
# 市场数据
curl https://global-insight-production.up.railway.app/api/v1/market

# 新闻数据
curl https://global-insight-production.up.railway.app/api/v1/news

# AI 洞察
curl https://global-insight-production.up.railway.app/api/v1/insights
```

---

## 📊 任务说明

| 任务 | 频率 | 功能 | 数据来源 |
|------|------|------|---------|
| fetch-market | 每 10 分钟 | 抓取股票/加密货币价格 | yfinance, CoinGecko |
| fetch-news | 每小时 | 抓取财经新闻 | RSS, Twitter |
| generate-insights | 每天 9 点 | 生成 AI 市场分析 | DashScope Qwen |
| build-graph | 每天 10 点 | 构建知识图谱 | 市场数据 + 新闻 |

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

**更新时间**: 2026-04-13 19:48
**状态**: 代码已部署，等待 Railway Cron 配置
