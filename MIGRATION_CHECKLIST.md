# Global Insight 迁移检查清单

## 📋 迁移前准备

- [ ] 备份当前数据库（已完成：`backup_20260410_171610.sql`, 3.3MB）
- [ ] 阅读 MIGRATE_TO_NEON.md
- [ ] 阅读 DEPLOY_VERCEL.md
- [ ] 准备 Neon 账号（https://neon.tech）
- [ ] 准备 GitHub 账号
- [ ] 准备 Vercel 账号
- [ ] 准备 DashScope API Key

---

## 🗄️ 数据库迁移

### 步骤 1: 创建 Neon 数据库

- [ ] 访问 https://neon.tech 并登录
- [ ] 创建新项目 `global-insight`
- [ ] 选择区域（推荐：AWS AP-East-1 香港）
- [ ] 复制连接字符串

### 步骤 2: 启用 pgvector

- [ ] 在 Neon SQL Editor 运行：`CREATE EXTENSION IF NOT EXISTS vector;`
- [ ] 验证：`SELECT * FROM pg_extension WHERE extname = 'vector';`

### 步骤 3: 导出数据

```bash
cd /root/global-insight
docker exec global-insight-db pg_dump -U jack -d finance_insight --no-owner --no-privileges > backup_full.sql
```

- [ ] 验证备份文件：`ls -lh backup_full.sql`

### 步骤 4: 导入到 Neon

**方法 A: 使用 psql**
```bash
psql '<NEON_CONNECTION_STRING>' < backup_full.sql
```

**方法 B: 使用 Web 界面**
- [ ] 在 Neon SQL Editor 粘贴 backup_full.sql 内容
- [ ] 运行导入

- [ ] 导入完成

### 步骤 5: 验证数据

在 Neon SQL Editor 运行：

```sql
SELECT COUNT(*) FROM market_data;  -- 应该返回 ~12989
SELECT COUNT(*) FROM news;         -- 应该返回 ~123
SELECT COUNT(*) FROM ai_insights;  -- 应该返回 ~2
```

- [ ] 数据量正确
- [ ] 向量数据正常：`SELECT vector_dims(embedding) FROM news LIMIT 1;`

---

## 🔧 GitHub 配置

### 步骤 1: 创建仓库

- [ ] 访问 https://github.com/new
- [ ] 创建仓库 `global-insight`
- [ ] 设为 Public 或 Private

### 步骤 2: 推送代码

```bash
cd /root/global-insight
./deploy-to-vercel.sh
```

或手动：

```bash
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/global-insight.git
git push -u origin main
```

- [ ] 代码已推送

### 步骤 3: 配置 Secrets

访问：https://github.com/YOUR_USERNAME/global-insight/settings/secrets/actions

添加以下 secrets：

- [ ] `DATABASE_URL` = `postgresql://user:password@host.neon.tech/finance_insight?sslmode=require`
- [ ] `DASHSCOPE_API_KEY` = `sk-xxx`

---

## 🚀 Vercel 部署

### 步骤 1: 登录 Vercel

```bash
vercel login
```

- [ ] 已登录

### 步骤 2: 关联项目

```bash
cd /root/global-insight
vercel link --repo
```

- [ ] 项目已关联

### 步骤 3: 配置环境变量

访问：https://vercel.com/dashboard → 你的项目 → Settings → Environment Variables

添加：

- [ ] `DATABASE_URL` (Production, Preview, Development)
- [ ] `DASHSCOPE_API_KEY` (Production, Preview, Development)

### 步骤 4: 部署

```bash
vercel --prod
```

- [ ] 部署成功
- [ ] 记录部署域名：`https://xxx.vercel.app`

---

## ✅ 验证

### API 测试

```bash
# 健康检查
curl https://YOUR_PROJECT.vercel.app/api/v1/health

# 市场数据
curl https://YOUR_PROJECT.vercel.app/api/v1/market

# 新闻数据
curl https://YOUR_PROJECT.vercel.app/api/v1/news?limit=5

# AI 洞察
curl https://YOUR_PROJECT.vercel.app/api/v1/insights

# 知识图谱
curl https://YOUR_PROJECT.vercel.app/api/v1/graph
```

- [ ] 健康检查通过
- [ ] 市场数据正常
- [ ] 新闻数据正常
- [ ] AI 洞察正常
- [ ] 知识图谱正常

### 前端测试

- [ ] 访问 `https://YOUR_PROJECT.vercel.app`
- [ ] 页面加载正常
- [ ] 知识图谱显示正常
- [ ] 数据筛选功能正常
- [ ] AI 洞察弹窗正常

### 定时任务测试

访问 Vercel Dashboard → 你的项目 → Cron Jobs

- [ ] 看到 4 个定时任务
- [ ] 状态正常
- [ ] 等待第一次执行，检查日志

---

## 🔄 回滚方案

如果部署失败，可以快速回滚：

### 方案 1: Vercel 回滚

```bash
vercel rollback
```

### 方案 2: 恢复本地部署

```bash
cd /root/global-insight
docker-compose down
docker-compose up -d
```

- [ ] 确认本地部署正常：`curl http://localhost:11279`

---

## 📊 迁移后监控

### 第一周

- [ ] 每天检查 Vercel 日志：`vercel logs --follow`
- [ ] 检查 Neon 使用量：https://console.neon.tech → Usage
- [ ] 验证定时任务执行正常
- [ ] 检查数据更新频率

### 长期监控

- [ ] 设置 Vercel 告警（Settings → Notifications）
- [ ] 设置 Neon 使用量告警
- [ ] 定期检查 GitHub Actions 执行记录

---

## 💰 费用跟踪

### 月度检查

- [ ] Vercel 使用量：< 100GB 带宽（免费）
- [ ] Neon 使用量：< 0.5GB 存储（免费）
- [ ] GitHub Actions: < 2000 分钟（免费）

预期月费用：**$0**

---

## 📝 备注

记录迁移过程中遇到的问题和解决方案：

```
日期：2026-04-10
问题：
解决：

日期：
问题：
解决：
```

---

## 🎯 完成标志

当所有复选框都打勾时，迁移完成！✅
