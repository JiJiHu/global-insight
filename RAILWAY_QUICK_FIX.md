# Railway 配置修复 ✅

## 问题原因
Railway 提示 "Could not find root directory: backend" 是因为项目结构需要调整。

## 已完成的修复

### 1️⃣ 创建 Python 包
已创建 `/root/global-insight/backend/__init__.py`，使 backend 成为可导入的 Python 包。

### 2️⃣ 更新 railway.toml
修改启动命令，从项目根目录运行：

```toml
[deploy]
startCommand = "uvicorn backend.api:app --host 0.0.0.0 --port $PORT"
```

## Railway 配置步骤

### 方案 A：不设置 Root Directory（推荐）

1. **不要设置 Root Directory**（保持为空）
2. **添加环境变量**：
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_FjNWRTQ2gl1o@ep-raspy-mode-amvgg8he-pooler.c-5.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require
   DASHSCOPE_API_KEY=<你的 API Key>
   PORT=8000
   ```
3. **触发部署**

### 方案 B：设置 Root Directory

如果你更倾向于设置 Root Directory：

1. **Settings → Root Directory** 设置为 `backend`
2. **修改 railway.toml** 启动命令为：
   ```toml
   startCommand = "uvicorn api:app --host 0.0.0.0 --port $PORT"
   ```
3. **添加环境变量**（同上）
4. **触发部署**

## 验证部署

部署完成后测试：
```bash
# 健康检查
curl https://<your-railway-url>.railway.app/api/v1/health

# 市场数据
curl https://<your-railway-url>.railway.app/api/v1/market
```

---

**最后更新**: 2026-04-13 12:40
**状态**: 配置已修复，待部署验证
