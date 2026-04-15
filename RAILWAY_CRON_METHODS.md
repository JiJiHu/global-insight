# Railway Cron 服务配置

## efficient-creativity (Cron 服务)

### 配置方式 1: 使用 Procfile

创建 `Procfile` 在根目录：

```
web: cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT
cron: python backend/cron_tasks.py fetch-market
```

然后在 Railway 控制台选择 "cron" 进程

### 配置方式 2: 使用 railway.toml (推荐)

在当前目录创建 `railway.cron.toml` 或在 railway.toml 中添加：

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python backend/cron_tasks.py fetch-market"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[cron]
schedule = "0 * * * *"
```

### 配置方式 3: 手动配置（当前）

访问：
```
https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/settings
```

手动配置：
1. **Start Command**: `python backend/cron_tasks.py fetch-market`
2. **Cron Schedule**: `0 * * * *`
3. **Variables**:
   - `DATABASE_URL`: `${{Postgres.DATABASE_URL}}`
   - `DASHSCOPE_API_KEY`: (已有)

---

## 其他 Cron 服务配置

### fetch-news
- Schedule: `0 6,18 * * *`
- Command: `python backend/cron_tasks.py fetch-news`

### generate-insights
- Schedule: `0 7 * * *`
- Command: `python backend/cron_tasks.py generate-insights`

### build-graph
- Schedule: `30 7,19 * * *`
- Command: `python backend/cron_tasks.py build-graph`
