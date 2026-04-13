# Railway 部署指南 - 手动配置

## ⚠️ 问题说明

GitHub 仓库推送遇到问题，需要在 Railway 控制台手动配置。

## 📋 Railway 配置步骤

### 方案 1：重新连接 GitHub 仓库（推荐）

1. **访问 Railway 项目**
   ```
   https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f
   ```

2. **删除当前服务**（可选）
   - Settings → Delete Service

3. **重新部署**
   - New → Deploy from GitHub Repo
   - 选择 `jijihu/global-insight` 仓库

4. **配置环境变量**
   ```
   DATABASE_URL = postgresql://neondb_owner:npg_FjNWRTQ2gl1o@ep-raspy-mode-amvgg8he-pooler.c-5.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require
   DASHSCOPE_API_KEY = <你的 API Key>
   PORT = 8000
   ```

5. **等待自动部署**

---

### 方案 2：使用 Railway CLI 部署

```bash
# 登录 Railway
railway login

# 进入项目目录
cd /root/global-insight

# 链接现有项目
railway link --project 5e1c61e5-8994-465c-ae6a-7ad52501206f

# 部署
railway deploy
```

---

## 🔧 本地代码已准备就绪

- ✅ `backend/__init__.py` - 已创建
- ✅ `railway.toml` - 配置已更新
- ✅ `requirements-railway.txt` - 依赖已优化
- ✅ `nixpacks.toml` - 构建配置已就绪

---

## ✅ 验证部署

部署成功后：
```bash
curl https://<your-railway-url>.railway.app/api/v1/health
```

---

**更新时间**: 2026-04-13 12:50
**状态**: 等待用户手动配置
