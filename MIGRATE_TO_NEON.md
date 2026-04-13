# 迁移到 Neon 数据库指南

## 步骤 1: 创建 Neon 数据库

1. 访问 https://neon.tech
2. 使用 GitHub 账号登录
3. 点击 "New Project"
4. 项目名称：`global-insight`
5. 选择区域：建议选择离你最近的（如 AWS AP-East-1 香港）
6. 点击 "Create Project"

## 步骤 2: 获取数据库连接字符串

1. 在 Neon Dashboard 中，点击你的项目
2. 点击 "Connection Details"
3. 复制 **Postgres connection string**
   - 格式：`postgresql://user:password@host.neon.tech/dbname?sslmode=require`
4. 保存这个字符串，后面会用到

## 步骤 3: 启用 pgvector 扩展

在 Neon Dashboard 中：
1. 点击 "SQL Editor"
2. 运行以下命令：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. 验证安装：
```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## 步骤 4: 导出当前数据库

在服务器上运行：

```bash
cd /root/global-insight

# 导出完整数据库（带结构 + 数据）
docker exec global-insight-db pg_dump -U jack -d finance_insight --no-owner --no-privileges > backup_full.sql

# 验证导出成功
ls -lh backup_full.sql
```

## 步骤 5: 导入到 Neon

### 方法 A: 使用 psql 命令行（推荐）

```bash
# 安装 postgresql-client（如果没有）
apt-get update && apt-get install -y postgresql-client

# 导入数据
psql '<YOUR_NEON_CONNECTION_STRING>' < backup_full.sql
```

### 方法 B: 使用 Neon 的 Web 界面

1. 在 Neon Dashboard 点击 "SQL Editor"
2. 复制 `backup_full.sql` 的内容
3. 粘贴到 SQL Editor 并运行

## 步骤 6: 验证数据

在 Neon SQL Editor 中运行：

```sql
-- 检查表
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- 检查市场数据数量
SELECT COUNT(*) FROM market_data;

-- 检查新闻数量
SELECT COUNT(*) FROM news;

-- 检查向量维度
SELECT vector_dims(embedding) FROM news LIMIT 1;
```

## 步骤 7: 配置环境变量

### 在 GitHub 配置：

1. 进入 GitHub 仓库 → Settings → Secrets and variables → Actions
2. 添加以下 secrets：

```
DATABASE_URL=postgresql://user:password@host.neon.tech/finance_insight?sslmode=require
DASHSCOPE_API_KEY=你的 DashScope API Key
```

### 在 Vercel 配置：

1. 进入 Vercel Dashboard → 你的项目 → Settings → Environment Variables
2. 添加同样的环境变量

## 步骤 8: 测试连接

在本地测试：

```bash
# 测试 Neon 连接
psql '<YOUR_NEON_CONNECTION_STRING>' -c "SELECT COUNT(*) FROM market_data;"
```

## 注意事项

### 1. 连接池

Neon 是 Serverless 数据库，建议使用连接池：

```python
# 在 backend/config.py 中
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

# 添加连接池参数
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # 自动检测断连
)
```

### 2. SSL 模式

Neon 强制要求 SSL，确保连接字符串包含 `?sslmode=require`

### 3. 自动休眠

Neon 在无连接 5 分钟后自动休眠，首次连接会有 ~500ms 冷启动延迟

### 4. 备份策略

建议保留本地数据库作为备份：

```bash
# 每天备份到本地
docker exec global-insight-db pg_dump -U jack finance_insight | gzip > backup_$(date +%Y%m%d).sql.gz
```

## 故障排查

### 问题：连接超时

```bash
# 检查网络连接
curl -I https://console.neon.tech

# 测试 SSL
psql '<YOUR_NEON_CONNECTION_STRING>' -c "\conninfo"
```

### 问题：pgvector 未安装

```sql
-- 在 Neon SQL Editor 运行
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证
\dx
```

### 问题：数据导入失败

```bash
# 分步导入
psql '<YOUR_NEON_CONNECTION_STRING>' < backup_full.sql 2>&1 | tee import.log

# 查看错误
grep ERROR import.log
```

## 费用估算

Neon 免费额度：
- ✅ 0.5 GB 存储（你的数据约 300MB）
- ✅ 每月 50 万行读取
- ✅ 自动休眠（不收费）

预计费用：**$0/月**（在免费额度内）

---

下一步：完成数据库迁移后，运行 `vercel --prod` 部署前端到 Vercel
