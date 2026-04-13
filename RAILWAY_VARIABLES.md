# Railway 环境变量配置清单

## 📋 必需的环境变量

请在 Railway 项目控制台中添加以下变量：

### 1. 数据库连接
```
Key: DATABASE_URL
Value: postgresql://neondb_owner:npg_FjNWRTQ2gl1o@ep-raspy-mode-amvgg8he-pooler.c-5.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require
```

### 2. DashScope API Key
```
Key: DASHSCOPE_API_KEY
Value: <你已配置的 API Key>
```

### 3. 端口（Railway 通常自动设置）
```
Key: PORT
Value: 8000
```

---

## 🔧 配置步骤

### 步骤 1: 进入项目页面
打开你的 Railway 项目：
https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/fee2b7f1-a3e5-4383-a7d2-c633fd4c83e9

### 步骤 2: 添加环境变量
1. 点击顶部导航栏的 **"Variables"** 标签
2. 点击 **"New Variable"** 按钮
3. 依次添加上述 3 个环境变量

### 步骤 3: 配置 Root Directory
1. 点击 **"Settings"** 标签
2. 找到 **"Root Directory"** 字段
3. 输入：`backend`
4. 保存设置

### 步骤 4: 触发重新部署
1. 返回 **"Deployments"** 标签
2. 点击 **"Deploy"** 或等待自动部署
3. 查看部署日志确认成功

---

## ✅ 验证部署

部署完成后，测试以下端点：

### 健康检查
```bash
curl https://<your-railway-url>.railway.app/api/v1/health
```

### 市场数据
```bash
curl https://<your-railway-url>.railway.app/api/v1/market
```

### 新闻数据
```bash
curl https://<your-railway-url>.railway.app/api/v1/news?limit=5
```

---

## 📊 预期响应示例

健康检查成功响应：
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

---

## 🆘 故障排查

### 构建失败
- 检查 `requirements-railway.txt` 是否正确
- 查看构建日志中的错误信息

### 启动失败
- 确认环境变量 `DATABASE_URL` 已正确设置
- 检查 `PORT` 变量是否存在

### 数据库连接失败
- 验证 Neon Database 连接字符串
- 确认 SSL 模式配置正确

---

**创建时间**: 2026-04-13 11:02
**项目**: Global Insight Railway Migration
