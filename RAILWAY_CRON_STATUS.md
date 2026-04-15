# Railway Cron 配置状态报告

**更新时间**: 2026-04-14 10:30  
**状态**: ⚠️ 部分完成

---

## ✅ 已完成的工作

### 1. Railway CLI 登录
- ✅ 已登录账号：Jiajie Hu (405936122@qq.com)
- ✅ 项目已找到：zestful-education
- ✅ global-insight 服务已在线

### 2. 浏览器登录
- ✅ GitHub 登录成功（已通过邮箱验证码 148187）
- ✅ Railway Dashboard 已访问
- ✅ 项目页面已打开：https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f

### 3. 代码准备
- ✅ `backend/cron_tasks.py` 已就绪，包含 4 个任务：
  - `fetch-market` - 市场数据抓取
  - `fetch-news` - 新闻抓取
  - `generate-insights` - AI 洞察生成
  - `build-graph` - 知识图谱构建

---

## ⚠️ Railway Cron 配置说明

Railway 的 Cron 配置方式已更新，现在需要通过以下方式配置：

### 方式 1：通过 Service 配置 Schedule（推荐）

1. 在项目页面点击 "Add" 按钮
2. 选择 "Empty Service" 或 "Docker Image"
3. 配置 Docker 镜像为：`global-insight-backend`（使用现有镜像）
4. 在服务设置中配置 **Schedule**：
   ```
   fetch-market: 0 * * * *
   fetch-news: 0 6,18 * * *
   generate-insights: 0 7 * * *
   build-graph: 30 7,19 * * *
   ```
5. 配置 Command：
   ```
   python backend/cron_tasks.py <task-name>
   ```

### 方式 2：使用 Railway Functions（新功能）

Railway 可能已迁移到 Functions 方式来处理定时任务。

---

## 📋 需要的 Cron 配置

| 任务名 | Schedule | Command |
|--------|----------|---------|
| fetch-market | `0 * * * *` | `python backend/cron_tasks.py fetch-market` |
| fetch-news | `0 6,18 * * *` | `python backend/cron_tasks.py fetch-news` |
| generate-insights | `0 7 * * *` | `python backend/cron_tasks.py generate-insights` |
| build-graph | `30 7,19 * * *` | `python backend/cron_tasks.py build-graph` |

---

## 🔧 当前本地 Cron（仍在运行）

```bash
# 查看当前配置
crontab -l | grep global-insight

# 输出：
0 * * * * docker exec global-insight-backend python3 /app/fetch_market_data.py
0 6,18 * * * docker exec global-insight-backend python3 /app/fetch_news_sources.py
0 7 * * * docker exec global-insight-backend python3 /app/generate_ai_insights_v3.py
30 7,19 * * * docker exec global-insight-backend python /app/build_knowledge_graph_v2.py
```

---

## 📝 下一步操作

由于 Railway 的 Cron 配置界面可能已更新，建议：

1. **查看 Railway 文档**：https://docs.railway.com/deploy/cron-jobs
2. **手动配置**：在 Railway 控制台按照最新方式配置 Cron
3. **验证配置**：配置完成后查看 Cron 日志确认执行成功

---

## 🆘 备选方案

如果 Railway Cron 配置复杂，可以：
1. 继续使用本地 Cron（当前运行正常）
2. 使用 GitHub Actions 定时触发
3. 使用其他 Cron 服务（如 Cron-job.org, EasyCron 等）

---

**当前状态**: 本地 Cron 正常运行，Railway Cron 待配置
