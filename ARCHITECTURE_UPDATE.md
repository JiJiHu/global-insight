# 架构更新 - 迁移到 Railway PostgreSQL

**日期**: 2026-04-17  
**目标**: 从 Neon 迁移到 Railway PostgreSQL

---

## 🏗️ 新架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Vercel    │────▶│   Railway    │────▶│ Railway          │
│  (前端静态)  │     │  (后端 API)   │     │ PostgreSQL       │
│             │     │              │     │ (数据库)          │
└─────────────┘     └──────────────┘     └──────────────────┘
```

---

## 📋 配置步骤

### 1. Railway PostgreSQL 数据库

**在 Railway 控制台**:
1. 登录 https://railway.app
2. 选择项目：`global-insight`
3. 点击 **New** → **Database** → **PostgreSQL**
4. 等待数据库创建完成
5. 点击数据库 → **Connect** → 复制 `DATABASE_URL`

**DATABASE_URL 格式**:
```
postgresql://postgres:密码@railway.internal:5432/railway?sslmode=require
```

---

### 2. Railway 环境变量

**在 Railway 控制台**:
1. 选择项目：`global-insight`
2. 点击 **Variables** 标签
3. 添加/更新环境变量：

```bash
DATABASE_URL=postgresql://postgres:xxx@railway.internal:5432/railway?sslmode=require
FINNHUB_API_KEY=d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g
DASHSCOPE_API_KEY=你的 DashScope API Key
```

---

### 3. Vercel 环境变量

**在 Vercel 控制台**:
1. 登录 https://vercel.com
2. 选择项目：`global-insight`
3. 点击 **Settings** → **Environment Variables**
4. 删除 Neon 相关变量
5. 添加：

```bash
NEXT_PUBLIC_API_URL=https://global-insight-production.up.railway.app
```

**注意**: Vercel 前端不需要数据库连接，API 请求会转发到 Railway 后端。

---

### 4. 更新 vercel.json

**当前配置已经正确**:
```json
{
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://global-insight-production.up.railway.app/api/$1"
    }
  ]
}
```

所有 API 请求都会代理到 Railway 后端。

---

## 🚀 部署流程

### Railway 后端
```bash
cd /root/global-insight
git push origin main
# Railway 会自动部署
```

### Vercel 前端
```bash
cd /root/global-insight
./deploy-vercel.sh
# 或使用 Vercel CLI
vercel --prod
```

---

## 📊 数据迁移（如需要）

如果 Neon 数据库已有数据，需要迁移到 Railway PostgreSQL：

### 1. 导出 Neon 数据
```bash
pg_dump "postgresql://neondb_owner:xxx@ep-raspy-mode-amvgg8he-pooler.c-5.us-east-1.aws.neon.tech/neondb" \
  --table=market_data --table=news \
  -f backup.sql
```

### 2. 导入 Railway PostgreSQL
```bash
psql "postgresql://postgres:xxx@railway.internal:5432/railway" \
  -f backup.sql
```

---

## ✅ 验证清单

### Railway 后端
- [ ] PostgreSQL 数据库已创建
- [ ] `DATABASE_URL` 环境变量已配置
- [ ] 后端服务正常运行
- [ ] Cron 任务正常执行
- [ ] 日志显示数据写入成功

### Vercel 前端
- [ ] 网站正常访问
- [ ] API 请求能获取数据
- [ ] 知识图谱正常显示
- [ ] AI 洞察正常显示

---

## 🔍 故障排查

### 问题 1: DATABASE_URL not set
**解决**: 在 Railway Variables 添加 `DATABASE_URL`

### 问题 2: Connection timeout
**解决**: 检查 Railway PostgreSQL 是否正常运行

### 问题 3: Table doesn't exist
**解决**: 运行 `python backend/create_tables.py` 创建表

### 问题 4: API 请求失败
**解决**: 检查 Vercel vercel.json 中的 API 代理配置

---

## 📝 环境变量对比

| 平台 | 变量 | 值 |
|------|------|-----|
| **Railway** | DATABASE_URL | Railway PostgreSQL 连接 |
| **Railway** | FINNHUB_API_KEY | d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g |
| **Railway** | DASHSCOPE_API_KEY | 你的密钥 |
| **Vercel** | NEXT_PUBLIC_API_URL | https://global-insight-production.up.railway.app |

---

*创建时间：2026-04-17 11:32*
