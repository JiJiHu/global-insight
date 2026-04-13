# Railway 部署配置指南

## ✅ 已完成配置
- [x] DashScope API Key 已配置
- [x] railway.toml 配置文件已创建
- [x] nixpacks.toml 构建配置已创建
- [x] requirements-railway.txt 依赖文件已准备

## 🔧 Railway 环境变量配置

### 必需的环境变量
在 Railway 控制台 → Variables 中添加以下变量：

```bash
# 数据库连接 (Neon Database)
DATABASE_URL=postgresql://neondb_owner:npg_FjNWRTQ2gl1o@ep-raspy-mode-amvgg8he-pooler.c-5.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require

# DashScope API Key (AI 功能)
DASHSCOPE_API_KEY=<已配置>

# 端口 (Railway 自动设置，但建议显式配置)
PORT=8000
```

### 可选的环境变量
```bash
# 日志级别
LOG_LEVEL=info

# 环境变量标识
ENVIRONMENT=production
```

## 📦 构建配置

### railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[environments]
[environments.production]
PYTHON_VERSION = "3.11"
```

### nixpacks.toml
```toml
[build]
[build.nix]
nix = ["python311", "postgresql"]
```

## 🚀 部署步骤

### 1. 连接 GitHub 仓库
1. 登录 Railway: https://railway.com
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择 `global-insight` 仓库

### 2. 配置服务
1. 选择部署 `backend` 目录作为 Root Directory
2. Railway 会自动识别 `railway.toml` 和 `nixpacks.toml`
3. 添加上述环境变量

### 3. 部署
1. 点击 "Deploy"
2. 等待构建完成（约 2-5 分钟）
3. 检查健康检查：`https://<your-railway-url>.railway.app/api/v1/health`

## 🗄️ 数据库迁移

### 方案 A: 使用现有 Neon 数据库
当前配置已连接到 Neon Database，数据已存在，无需迁移。

### 方案 B: 导出并导入数据（如需迁移）
```bash
# 1. 从本地导出
docker exec global-insight-db pg_dump -U jack -d finance_insight > backup.sql

# 2. 导入到 Neon
psql "postgresql://neondb_owner:npg_FjNWRTQ2gl1o@ep-raspy-mode-amvgg8he-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require" < backup.sql
```

## ✅ 验证清单

部署完成后，验证以下功能：

- [ ] 健康检查：`GET /api/v1/health`
- [ ] 市场数据：`GET /api/v1/market`
- [ ] 新闻数据：`GET /api/v1/news?limit=5`
- [ ] AI 洞察：`GET /api/v1/insights`
- [ ] 知识图谱：`GET /api/v1/graph`

## 🔗 域名配置（可选）

1. Railway 控制台 → Settings → Domains
2. 添加自定义域名
3. 配置 DNS CNAME 记录

## 📊 监控和日志

- Railway 控制台 → Deployments → View Logs
- 实时监控部署状态和错误日志

## 🛠️ 故障排查

### 构建失败
1. 检查 `requirements-railway.txt` 是否完整
2. 确认 `nixpacks.toml` 配置正确
3. 查看构建日志中的错误信息

### 启动失败
1. 检查环境变量是否正确配置
2. 验证数据库连接字符串
3. 检查健康检查路径是否正确

### 数据库连接失败
1. 确认 Neon Database 连接字符串正确
2. 检查 SSL 模式配置
3. 验证数据库权限

---

**最后更新**: 2026-04-13
**状态**: 配置完成，待部署验证
