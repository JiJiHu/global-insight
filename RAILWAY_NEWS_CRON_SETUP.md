# 🚂 Railway 云端定时任务配置指南

## ✅ 已完成

### 1. 新闻抓取脚本
- **文件**: `/root/global-insight/backend/railway_fetch_news.py`
- **功能**: 每 30 分钟抓取所有新闻源并写入 Neon 数据库
- **支持来源**:
  - Finnhub API (Reuters, CNBC, Bloomberg)
  - RSS (中国新闻网，Bloomberg, Investing.com, CNBC)
  - Twitter (通过 Nitter: Reuters, Bloomberg, WSJ, CNBC, FT)
  - GitHub Blog

### 2. 依赖配置
- **文件**: `/root/global-insight/nixpacks.toml`
- **已添加**: `feedparser`, `psycopg2-binary`

### 3. Railway 环境变量
已配置：
- ✅ `DATABASE_URL` (Neon 数据库)
- ✅ `DASHSCOPE_API_KEY`

## 📋 Railway 配置步骤

### 方法 1: Railway 控制台配置（推荐）

1. **登录 Railway**
   - https://railway.app/
   - 项目：`zestful-education`
   - 服务：`efficient-creativity`

2. **添加 Cron 定时任务**
   - 进入服务 → **Settings** → **Cron**
   - 点击 **Add Cron Job**
   - 配置：
     ```
     Name: news-fetcher
     Schedule: */30 * * * *
     Command: python backend/railway_fetch_news.py
     ```

3. **验证环境变量**
   - Settings → Variables
   - 确保有以下变量：
     - `DATABASE_URL` ✅ (已有)
     - `FINNHUB_API_KEY` (可选，脚本中已硬编码)

### 方法 2: Railway CLI 配置

```bash
# 登录 Railway
railway login

# 进入项目
cd /root/global-insight

# 部署更新
railway deploy

# 添加 Cron 任务
railway cron add --schedule "*/30 * * * *" --command "python backend/railway_fetch_news.py"
```

## 📊 当前状态

| 项目 | 状态 |
|------|------|
| 脚本 | ✅ 已创建 |
| 依赖 | ✅ 已配置 |
| 数据库 | ✅ Neon 已连接 |
| Railway Cron | ⏳ 待配置 |

## 🔧 测试命令

本地测试：
```bash
cd /root/global-insight/backend
python3 railway_fetch_news.py
```

Railway 测试：
```bash
cd /root/global-insight
railway run python backend/railway_fetch_news.py
```

## 📝 注意事项

1. **Nitter 稳定性**: Nitter 实例可能不稳定，如果失败会自动跳过
2. **数据库连接**: 使用 Railway 提供的 `DATABASE_URL` 环境变量
3. **执行时间**: 完整抓取约 30-60 秒，远小于 Railway 的 15 分钟限制
4. **日志查看**: Railway 控制台 → Deployments → 查看日志

## 🎯 下一步

1. 在 Railway 控制台添加 Cron 任务
2. 等待第一次执行（30 分钟内）
3. 检查 Neon 数据库确认数据更新
4. 验证前端页面显示最新新闻
