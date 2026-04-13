# Railway 最终配置方案 ✅

## Railway 控制台配置步骤

### 1️⃣ Settings → Root Directory
设置为：**backend**

### 2️⃣ Variables → 添加环境变量
```
DATABASE_URL = postgresql://neondb_owner:npg_FjNWRTQ2gl1o@ep-raspy-mode-amvgg8he-pooler.c-5.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require

DASHSCOPE_API_KEY = <你的 API Key>

PORT = 8000
```

### 3️⃣ Deployments → 触发部署

---

## 本地配置说明

### railway.toml（已更新）
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### 项目结构
```
global-insight/
├── backend/          ← Root Directory 设置为这个
│   ├── __init__.py   ← 已创建
│   ├── api.py        ← 主 API 文件
│   ├── requirements-railway.txt
│   └── ...
├── railway.toml      ← 项目根目录
└── nixpacks.toml     ← 项目根目录
```

---

## 验证部署

部署成功后测试：
```bash
curl https://<your-railway-url>.railway.app/api/v1/health
```

---

**更新时间**: 2026-04-13 12:48
**状态**: 等待 Railway 配置完成
