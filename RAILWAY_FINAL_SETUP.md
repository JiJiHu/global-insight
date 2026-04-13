# Railway 最终配置指南 ✅

## 📋 配置状态

- [x] railway.toml 已创建
- [x] nixpacks.toml 已创建
- [x] requirements-railway.txt 已优化（精简依赖）
- [x] 代码已准备就绪
- [ ] 环境变量待配置（需手动）
- [ ] Root Directory 待配置（需手动）

---

## 🔧 手动配置步骤（5 分钟）

### 步骤 1: 登录 Railway

1. 访问：https://railway.com/login
2. 使用 GitHub 账号登录

### 步骤 2: 打开项目

访问你的项目页面：
```
https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/fee2b7f1-a3e5-4383-a7d2-c633fd4c83e9?environmentId=9bb9edca-2233-486d-a9a2-edf3ebe1f6af
```

### 步骤 3: 添加环境变量

1. 点击顶部 **"Variables"** 标签
2. 点击 **"New Variable"** 按钮
3. 依次添加以下 3 个变量：

#### 变量 1: DATABASE_URL
```
Key: DATABASE_URL
Value: postgresql://neondb_owner:npg_FjNWRTQ2gl1o@ep-raspy-mode-amvgg8he-pooler.c-5.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require
```

#### 变量 2: DASHSCOPE_API_KEY
```
Key: DASHSCOPE_API_KEY
Value: <填写你的 DashScope API Key>
```

#### 变量 3: PORT
```
Key: PORT
Value: 8000
```

### 步骤 4: 配置 Root Directory

1. 点击 **"Settings"** 标签
2. 找到 **"Root Directory"** 字段
3. 输入：`backend`
4. 按 Enter 保存

### 步骤 5: 触发部署

1. 返回 **"Deployments"** 标签
2. Railway 会自动检测到配置变更并开始部署
3. 如果没有自动部署，点击 **"Deploy"** 按钮

---

## ✅ 验证部署

### 等待部署完成（约 2-5 分钟）

部署成功后，你会看到绿色的 ✅ 标记和部署 URL。

### 测试 API 端点

**1. 健康检查**
```bash
curl https://<your-railway-url>.railway.app/api/v1/health
```

预期响应：
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-04-13T...",
  "stats": {
    "news_count": 123,
    "market_count": 12989
  }
}
```

**2. 市场数据**
```bash
curl https://<your-railway-url>.railway.app/api/v1/market
```

**3. 新闻数据**
```bash
curl https://<your-railway-url>.railway.app/api/v1/news?limit=5
```

**4. AI 洞察**
```bash
curl https://<your-railway-url>.railway.app/api/v1/insights
```

---

## 🆘 故障排查

### 构建失败

**查看构建日志：**
1. Deployments 标签 → 点击失败的部署
2. 查看 "Build" 日志

**常见原因：**
- `requirements-railway.txt` 依赖问题
- Python 版本不匹配

**解决方案：**
- 检查构建日志中的错误信息
- 确认 `nixpacks.toml` 配置正确

### 启动失败

**查看运行日志：**
1. Deployments 标签 → 点击部署
2. 查看 "Deploy" 日志

**常见原因：**
- 环境变量未配置
- 数据库连接失败

**解决方案：**
- 确认所有环境变量已正确添加
- 检查 DATABASE_URL 格式

### 数据库连接失败

**检查项：**
1. DATABASE_URL 是否完整复制（包括所有参数）
2. Neon Database 是否可访问
3. SSL 模式是否正确配置

---

## 📊 项目信息

- **项目名称**: Global Insight
- **服务 ID**: fee2b7f1-a3e5-4383-a7d2-c633fd4c83e9
- **环境 ID**: 9bb9edca-2233-486d-a9a2-edf3ebe1f6af
- **数据库**: Neon PostgreSQL (已有数据)
- **API Key**: DashScope (AI 功能)

---

## 📝 下一步

部署完成后：

1. ✅ 测试所有 API 端点
2. ✅ 配置自定义域名（可选）
3. ✅ 设置自动部署（连接 GitHub）
4. ✅ 配置监控和告警

---

**创建时间**: 2026-04-13 11:20
**状态**: 待手动配置环境变量
