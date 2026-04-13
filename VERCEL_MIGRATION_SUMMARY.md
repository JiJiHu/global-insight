# Global Insight - Vercel 迁移总结

> **创建时间**: 2026-04-10  
> **状态**: 准备就绪，等待执行  
> **预计费用**: $0/月（免费额度内）

---

## 📦 已创建的文件

### 📖 文档

| 文件 | 用途 |
|------|------|
| `MIGRATE_TO_NEON.md` | Neon 数据库迁移完整指南 |
| `DEPLOY_VERCEL.md` | Vercel 部署完整指南 |
| `MIGRATION_CHECKLIST.md` | 迁移检查清单（逐步打勾） |
| `VERCEL_MIGRATION_SUMMARY.md` | 本文档（总结） |

### ⚙️ 配置文件

| 文件 | 用途 |
|------|------|
| `vercel.json` | Vercel 项目配置（API 路由 + Cron Jobs） |
| `.github/workflows/cron.yml` | GitHub Actions 定时任务（备选方案） |
| `.gitignore` | Git 忽略文件配置 |

### 🐍 代码文件

| 文件 | 用途 |
|------|------|
| `backend/vercel_cron.py` | Vercel Cron 专用 API 端点 |
| `backend/api.py` | 已更新，集成 cron 路由 |

### 🚀 部署脚本

| 文件 | 用途 |
|------|------|
| `deploy-to-vercel.sh` | 一键部署脚本（交互式） |

---

## 🎯 迁移架构

```
┌─────────────────────────────────────────────────────┐
│  GitHub Actions / Vercel Cron (定时任务)             │
│  - 每 6 小时：抓取市场数据                             │
│  - 每天 8 点：抓取新闻                                 │
│  - 每天 9 点：生成 AI 洞察                             │
│  - 每天 10 点：构建知识图谱                           │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS API
                   ▼
┌─────────────────────────────────────────────────────┐
│  Neon PostgreSQL (带 pgvector)                       │
│  - 免费 0.5GB 存储                                    │
│  - 支持向量搜索                                       │
│  - 自动休眠                                           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Vercel (前端 + API)                                 │
│  - 静态文件 CDN                                       │
│  - Serverless Functions (Python/FastAPI)            │
│  - 全球边缘网络                                       │
└─────────────────────────────────────────────────────┘
```

---

## 📋 执行步骤

### 快速开始（3 步）

```bash
# 1. 迁移数据库到 Neon
#    参考：MIGRATE_TO_NEON.md

# 2. 运行部署脚本
cd /root/global-insight
./deploy-to-vercel.sh

# 3. 配置环境变量
#    - GitHub Secrets
#    - Vercel Environment Variables
```

### 详细步骤

参考 `MIGRATION_CHECKLIST.md`，逐步完成并打勾

---

## 🔑 需要准备的密钥

### 1. Neon 数据库连接字符串

格式：
```
postgresql://user:password@host.neon.tech/finance_insight?sslmode=require
```

获取方式：
1. 访问 https://neon.tech
2. 创建项目
3. Connection Details → 复制连接字符串

### 2. DashScope API Key

格式：
```
sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

获取方式：
1. 访问 https://dashscope.console.aliyun.com
2. API Key Management → 创建/复制 Key

---

## ⏰ 定时任务配置

已在 `vercel.json` 中配置：

| 任务 | Cron 表达式 | 频率 |
|------|-----------|------|
| 抓取市场数据 | `0 */6 * * *` | 每 6 小时 |
| 抓取新闻 | `0 8 * * *` | 每天 8 点 |
| 生成 AI 洞察 | `0 9 * * *` | 每天 9 点 |
| 构建知识图谱 | `0 10 * * *` | 每天 10 点 |

**注意**: Vercel Hobby 计划限制每天至少执行 1 次，上述配置符合要求

---

## ✅ 验证命令

### 部署后测试

```bash
# 替换 YOUR_PROJECT 为你的 Vercel 项目域名

# 健康检查
curl https://YOUR_PROJECT.vercel.app/api/v1/health

# 市场数据
curl https://YOUR_PROJECT.vercel.app/api/v1/market

# 新闻
curl https://YOUR_PROJECT.vercel.app/api/v1/news?limit=5

# AI 洞察
curl https://YOUR_PROJECT.vercel.app/api/v1/insights

# 知识图谱
curl https://YOUR_PROJECT.vercel.app/api/v1/graph
```

### 查看日志

```bash
vercel logs --follow
```

---

## 🔄 回滚方案

### 如果部署失败

**方案 1: Vercel 回滚**
```bash
vercel rollback
```

**方案 2: 恢复本地部署**
```bash
cd /root/global-insight
docker-compose down
docker-compose up -d
```

本地部署验证：
```bash
curl http://localhost:11279
```

---

## 💰 费用对比

### 当前（本地 Docker）

| 项目 | 费用 |
|------|------|
| 服务器 | 已有（ECS） |
| 数据库 | 本地 PostgreSQL |
| 域名 | 公网 IP:11279 |
| **总计** | **服务器成本** |

### 迁移后（Vercel + Neon）

| 项目 | 免费额度 | 预计使用 | 费用 |
|------|---------|---------|------|
| Vercel | 100GB/月 | ~10GB | ✅ $0 |
| Neon | 0.5GB | ~300MB | ✅ $0 |
| GitHub Actions | 2000 分钟/月 | ~500 分钟 | ✅ $0 |
| **总计** | | | **$0/月** |

**节省**: 无需占用服务器资源，可关闭相关 Docker 容器

---

## ⚠️ 注意事项

### 1. 数据库连接

Neon 是 Serverless 数据库，有冷启动延迟（~500ms）
- ✅ 已配置连接池
- ✅ 已设置 `pool_pre_ping=True`

### 2. API 超时

Vercel Serverless Functions 超时限制：
- Hobby: 10 秒
- Pro: 60 秒

已优化：
- ✅ 复杂任务放到定时任务（Cron Jobs）
- ✅ API 端点保持轻量

### 3. 数据一致性

迁移期间：
- [ ] 停止本地定时任务（避免双写）
- [ ] 确认数据同步完成
- [ ] 切换流量到 Vercel

---

## 📞 支持资源

### 官方文档

- [Vercel Cron Jobs](https://vercel.com/docs/cron-jobs)
- [Neon PostgreSQL](https://neon.tech/docs)
- [Vercel Python Functions](https://vercel.com/docs/functions/serverless-functions/runtimes/python)

### 项目文档

- `MIGRATE_TO_NEON.md` - 数据库迁移
- `DEPLOY_VERCEL.md` - Vercel 部署
- `MIGRATION_CHECKLIST.md` - 检查清单

### 故障排查

遇到问题？查看：
1. Vercel Dashboard → Deployments → 查看日志
2. Neon Dashboard → SQL Editor → 测试连接
3. GitHub → Actions → 查看定时任务执行记录

---

## 🎉 迁移完成后

### 可以做的事情

1. ✅ 关闭本地 Docker 容器（节省资源）
   ```bash
   docker-compose down
   ```

2. ✅ 配置自定义域名（可选）
   - 在 Vercel Dashboard → Domains
   - 添加你的域名

3. ✅ 设置监控告警
   - Vercel Settings → Notifications
   - Neon Usage → Alerts

4. ✅ 分享你的应用
   - 前端：`https://YOUR_PROJECT.vercel.app`
   - API: `https://YOUR_PROJECT.vercel.app/api/v1/health`

---

## 📝 更新日志

| 日期 | 操作 | 状态 |
|------|------|------|
| 2026-04-10 | 创建迁移文档和配置 | ✅ 完成 |
| 2026-04-10 | 创建部署脚本 | ✅ 完成 |
| 2026-04-10 | 备份数据库（3.3MB） | ✅ 完成 |
| 待执行 | 迁移到 Neon | ⏳ 等待 |
| 待执行 | 部署到 Vercel | ⏳ 等待 |

---

**准备好开始了吗？**

运行：
```bash
cd /root/global-insight
./deploy-to-vercel.sh
```

或者按照 `MIGRATION_CHECKLIST.md` 逐步执行。

Good luck! 🚀
