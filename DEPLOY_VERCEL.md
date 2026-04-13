# 部署到 Vercel 完整指南

## 前置条件

✅ 已完成数据库迁移到 Neon（参考 MIGRATE_TO_NEON.md）
✅ 已创建 GitHub 账号
✅ 已安装 Vercel CLI (`npm install -g vercel`)

---

## 步骤 1: 推送到 GitHub

### 1.1 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名：`global-insight`
3. 设为 **Public** 或 **Private**（根据你的需求）
4. **不要** 勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

### 1.2 推送代码

```bash
cd /root/global-insight

# 配置 Git（如果还没有）
git config user.email "your-email@example.com"
git config user.name "Your Name"

# 初始化仓库（如果还没有）
git init
git add -A
git commit -m "Initial commit - Vercel deployment"
git branch -M main

# 关联 GitHub 仓库
git remote add origin https://github.com/YOUR_USERNAME/global-insight.git

# 推送
git push -u origin main
```

---

## 步骤 2: 配置 GitHub Secrets

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**

添加以下 secrets：

| Name | Value |
|------|-------|
| `DATABASE_URL` | `postgresql://user:password@host.neon.tech/finance_insight?sslmode=require` |
| `DASHSCOPE_API_KEY` | 你的 DashScope API Key |

---

## 步骤 3: 部署到 Vercel

### 3.1 登录 Vercel

```bash
vercel login
```

选择 GitHub 登录

### 3.2 关联 GitHub 仓库

```bash
cd /root/global-insight
vercel link
```

- 选择 **Import Git Repository**
- 选择你的 `global-insight` 仓库
- 点击 **Connect**

### 3.3 配置环境变量

在 Vercel Dashboard 中：

1. 进入你的项目
2. 点击 **Settings** → **Environment Variables**
3. 添加以下变量：

| Key | Value | Environments |
|-----|-------|--------------|
| `DATABASE_URL` | `postgresql://...` | Production, Preview, Development |
| `DASHSCOPE_API_KEY` | `sk-xxx` | Production, Preview, Development |

### 3.4 首次部署

```bash
vercel --prod
```

---

## 步骤 4: 配置自定义域名（可选）

### 4.1 在 Vercel 添加域名

1. 进入 Vercel Dashboard → 你的项目
2. 点击 **Domains**
3. 输入你的域名：`global-insight.yourdomain.com`
4. 点击 **Add**

### 4.2 配置 DNS

在你的域名注册商处添加：

```
类型：CNAME
主机：global-insight
值：cname.vercel-dns.com
TTL: 自动
```

### 4.3 验证

等待 DNS 传播（通常 5-30 分钟），然后访问你的域名

---

## 步骤 5: 配置定时任务

### 方案 A: 使用 Vercel Cron（推荐）

已在 `vercel.json` 中配置好：

```json
"crons": [
  {"path": "/api/v1/cron/fetch-market", "schedule": "0 */6 * * *"},
  {"path": "/api/v1/cron/fetch-news", "schedule": "0 8 * * *"},
  {"path": "/api/v1/cron/generate-insights", "schedule": "0 9 * * *"},
  {"path": "/api/v1/cron/build-graph", "schedule": "0 10 * * *"}
]
```

部署后自动生效！

### 方案 B: 使用 GitHub Actions

已在 `.github/workflows/cron.yml` 中配置好

---

## 步骤 6: 验证部署

### 6.1 检查 API

```bash
# 替换为你的 Vercel 域名
curl https://your-project.vercel.app/api/v1/health
```

预期响应：
```json
{
  "status": "healthy",
  "database": "connected",
  "stats": {
    "news_count": 123,
    "market_count": 12989
  }
}
```

### 6.2 检查前端

访问：`https://your-project.vercel.app`

应该能看到知识图谱界面

### 6.3 检查定时任务

在 Vercel Dashboard：
1. 进入你的项目
2. 点击 **Cron Jobs**（左侧菜单）
3. 查看所有定时任务状态

---

## 故障排查

### 问题 1: 部署失败 - 数据库连接错误

**原因**: 环境变量未正确配置

**解决**:
```bash
vercel env ls  # 检查环境变量
vercel env add DATABASE_URL  # 添加缺失的变量
```

### 问题 2: API 返回 500 错误

**原因**: 依赖缺失或 pgvector 未安装

**解决**:
1. 检查 Neon 数据库是否已启用 pgvector
2. 在 Vercel 查看部署日志：`vercel logs`

### 问题 3: 静态资源 404

**原因**: 前端文件路径问题

**解决**:
```bash
# 检查 frontend 目录结构
ls -la /root/global-insight/frontend/

# 确保 index.html 在根目录
```

### 问题 4: CORS 错误

**解决**: 已在 `vercel.json` 中配置 CORS headers，重新部署即可

---

## 费用估算

| 服务 | 免费额度 | 预计使用 | 费用 |
|------|---------|---------|------|
| **Vercel Hobby** | 100GB 带宽 | ~10GB | ✅ $0 |
| **Neon** | 0.5GB 存储 | ~300MB | ✅ $0 |
| **GitHub Actions** | 2000 分钟/月 | ~500 分钟 | ✅ $0 |
| **总计** | | | **$0/月** |

---

## 回滚方案

如果部署出现问题，可以快速回滚：

### 回滚到上一个版本

```bash
vercel rollback
```

### 恢复本地 Docker 部署

```bash
cd /root/global-insight
docker-compose down
docker-compose up -d
```

---

## 下一步

部署完成后：

1. ✅ 测试所有 API 端点
2. ✅ 验证定时任务正常运行
3. ✅ 监控 Vercel Dashboard 的日志
4. ✅ 设置告警（可选）

有任何问题，查看 Vercel 日志：
```bash
vercel logs --follow
```
