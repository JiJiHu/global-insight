# Railway Cron 配置 - 待完成事项

**更新日期**: 2026-04-14 11:57  
**状态**: 配置中

---

## ✅ 已完成

### 1. Cron 服务配置
- ✅ 服务名称: efficient-creativity
- ✅ Cron Schedule: `0 * * * *` (每小时执行)
- ✅ 已保存并部署

### 2. 环境变量
- ✅ DATABASE_URL: 已添加 (引用 ${{Postgres.DATABASE_URL}})

---

## ⚠️ 待完成

### 1. 添加 DASHSCOPE_API_KEY
在 Variables 页面添加：
- **Variable Name**: DASHSCOPE_API_KEY
- **Variable Value**: 你的 DashScope API Key

### 2. 配置 Docker 镜像
在 Settings 页面连接 Docker 镜像

### 3. 创建其他 Cron 服务
需要创建 3 个额外的 Cron 服务：

| 服务名称 | Schedule | 用途 |
|----------|----------|------|
| fetch-news | `0 6,18 * * *` | 新闻抓取 |
| generate-insights | `0 7 * * *` | AI 洞察 |
| build-graph | `30 7,19 * * *` | 知识图谱 |

---

## 🔧 手动配置步骤

### 添加 DASHSCOPE_API_KEY

1. 访问: https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/variables
2. 点击 "New Variable"
3. 输入:
   - Variable Name: `DASHSCOPE_API_KEY`
   - Variable Value: 你的 API Key
4. 点击 "Add"
5. 点击 "Deploy"

### 配置 Docker 镜像

1. 访问 Settings 页面
2. 在 Deploy 部分配置 Docker 镜像
3. 设置 Command: `python backend/cron_tasks.py fetch-market`

---

## 📋 本地 Cron 仍在运行

```bash
# 查看当前配置
crontab -l | grep global-insight
```

---

**注意**: 由于浏览器工具的交互超时问题，部分配置需要手动完成。