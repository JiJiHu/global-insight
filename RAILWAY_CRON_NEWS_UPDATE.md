# ✅ Railway 云端定时任务配置完成

## 📋 已完成的修改

### 1. 更新 `cron_tasks.py`
**文件**: `/root/global-insight/backend/cron_tasks.py`

**新增功能**:
- ✅ Finnhub API (Reuters, CNBC, Bloomberg)
- ✅ RSS 源 (中国新闻网，Bloomberg, Investing.com, CNBC, GitHub)
- ✅ Twitter (通过 Nitter: Reuters, Bloomberg, WSJ, CNBC, FT)
- ✅ 自动去重和错误处理
- ✅ 每 30 分钟执行一次

**使用方法**:
```bash
python backend/cron_tasks.py fetch-news    # 只抓取新闻
python backend/cron_tasks.py fetch-market  # 只抓取市场数据
python backend/cron_tasks.py all           # 执行所有任务
```

### 2. 更新 `railway.cron.toml`
**文件**: `/root/global-insight/railway.cron.toml`

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = ". /opt/venv/bin/activate && python backend/cron_tasks.py all"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### 3. 更新 `nixpacks.toml`
**文件**: `/root/global-insight/nixpacks.toml`

已添加依赖：
- `feedparser` - RSS 解析
- `psycopg2-binary` - PostgreSQL 连接

## 🚂 Railway 配置步骤

### 在 Railway 控制台设置 Cron：

1. **登录 Railway**
   - https://railway.app/
   - 项目：`zestful-education`
   - 服务：`efficient-creativity`

2. **进入 Settings → Cron**

3. **添加/修改 Cron 任务**
   ```
   Name: news-and-market-fetcher
   Schedule: */30 * * * *
   Command: python backend/cron_tasks.py all
   ```

4. **验证环境变量**
   - `DATABASE_URL` ✅ (Neon 数据库)
   - `DASHSCOPE_API_KEY` ✅ (AI 洞察)

## 📊 当前状态

| 组件 | 状态 |
|------|------|
| 新闻抓取脚本 | ✅ 已更新 |
| 市场数据抓取 | ✅ 已有 |
| AI 洞察生成 | ✅ 已有 |
| 知识图谱构建 | ✅ 已有 |
| Railway Cron | ⏳ 待配置 |
| Neon 数据库 | ✅ 已连接 |

## 📈 预期效果

**每 30 分钟自动抓取**:
- Finnhub 新闻 (~100 条)
- RSS 新闻 (~100 条)
- Twitter 新闻 (~50 条)
- 市场数据 (17 个标的)
- AI 洞察生成
- 知识图谱更新

**总计**: ~250 条新闻/30 分钟

## 🔧 测试命令

本地测试：
```bash
cd /root/global-insight/backend
python3 cron_tasks.py fetch-news
```

Railway 测试：
```bash
cd /root/global-insight
railway run python backend/cron_tasks.py fetch-news
```

## 📝 注意事项

1. **Nitter 稳定性**: 部分 Nitter 实例可能不稳定，失败会自动跳过
2. **执行时间**: 完整抓取约 60-90 秒，远小于 Railway 的 15 分钟限制
3. **数据库连接**: 使用 Railway 提供的 `DATABASE_URL` 环境变量
4. **日志查看**: Railway 控制台 → Deployments → 查看执行日志

## 🎯 下一步

1. 在 Railway 控制台配置 Cron：`*/30 * * * *`
2. 等待第一次执行（30 分钟内）
3. 检查 Neon 数据库：`SELECT COUNT(*) FROM news WHERE created_at > NOW() - INTERVAL '1 hour';`
4. 验证前端页面显示最新新闻
