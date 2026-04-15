# Railway Cron 配置完成报告

**更新时间**: 2026-04-14 10:45  
**状态**: ⚠️ 配置中（需要手动完成）

---

## ✅ 已完成的工作

### 1. 账号登录
- ✅ Railway CLI 已登录：Jiajie Hu (405936122@qq.com)
- ✅ GitHub 授权完成（验证码：148187）
- ✅ 项目已访问：https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f

### 2. 服务创建
- ✅ 已创建新服务：`efficient-creativity`
- ✅ 已进入 Settings 页面
- ✅ 已找到 Cron Schedule 配置项

### 3. 代码准备
- ✅ `backend/cron_tasks.py` 已就绪
- ✅ 包含 4 个任务函数

---

## ⚠️ 需要手动完成的部分

由于 Railway 界面交互复杂，以下步骤需要手动完成：

### 步骤 1: 配置 Docker 镜像

在 `efficient-creativity` 服务的 Settings 页面：
1. 找到 "Deploy" 部分
2. 点击 "Connect Image" 或 "Docker Image"
3. 输入镜像名称：`global-insight-backend`
4. 或者使用现有镜像的 URL

### 步骤 2: 配置 Cron Schedule

在 Settings 页面的 "Cron Schedule" 部分：
1. 点击 "Add Schedule"
2. 输入 Cron 表达式：`0 * * * *`（每小时）
3. 配置 Command：`python backend/cron_tasks.py fetch-market`

### 步骤 3: 配置环境变量

在 "Variables" 标签页添加：
```
DATABASE_URL=postgresql://...
DASHSCOPE_API_KEY=sk-...
PORT=8000
```

### 步骤 4: 部署服务

点击 "Deploy" 按钮部署服务

---

## 📋 需要创建的 Cron 任务

| 任务名 | Schedule | Command |
|--------|----------|---------|
| fetch-market | `0 * * * *` | `python backend/cron_tasks.py fetch-market` |
| fetch-news | `0 6,18 * * *` | `python backend/cron_tasks.py fetch-news` |
| generate-insights | `0 7 * * *` | `python backend/cron_tasks.py generate-insights` |
| build-graph | `30 7,19 * * *` | `python backend/cron_tasks.py build-graph` |

**注意**：每个 Cron 任务需要创建一个独立的服务。

---

## 🔧 当前本地 Cron（正常运行）

```bash
# 查看配置
crontab -l | grep global-insight

# 输出：
0 * * * * docker exec global-insight-backend python3 /app/fetch_market_data.py
0 6,18 * * * docker exec global-insight-backend python3 /app/fetch_news_sources.py
0 7 * * * docker exec global-insight-backend python3 /app/generate_ai_insights_v3.py
30 7,19 * * * docker exec global-insight-backend python /app/build_knowledge_graph_v2.py
```

**日志位置**：
- `/var/log/global-insight/market.log`
- `/var/log/global-insight/news-sources.log`
- `/var/log/global-insight/ai-insights.log`
- `/var/log/global-insight/graph.log`

---

## 📝 建议

由于 Railway Cron 配置需要创建 4 个独立服务，比较复杂，建议：

1. **继续使用本地 Cron**（当前运行正常）
2. **或者手动完成 Railway 配置**：
   - 访问：https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/settings
   - 按照上述步骤配置

---

**当前状态**: 本地 Cron 正常运行，Railway 配置已准备就绪
