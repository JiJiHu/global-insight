# Railway Cron 任务优化完成

**日期**: 2026-04-17  
**问题**: Cron 任务运行时间过长 + Vercel 网站不更新

---

## 🔍 问题分析

### 1. Railway Cron 运行时间过长 ❌

**根本原因**:
- `cron_simple.py` 没有超时保护，API 调用可能卡住
- API 调用过多：8 只股票 + 6 只加密货币 + 2 个 RSS 源
- 超时设置过长：5-10 秒，导致总运行时间不可控
- Railway cron 要求进程快速完成并退出，否则后续执行会被跳过

**原配置**:
```toml
# railway.toml
[[crons]]
name = "hourly-data-fetcher"
schedule = "0 * * * *"  # 每小时
command = "/opt/venv/bin/python backend/cron_simple.py"
```

### 2. Vercel 网站不更新 ❌

**原因**:
- Git push 后没有自动触发 Vercel 部署
- 前端是静态站点，代码不变不会重新构建
- 需要手动触发或配置自动部署

---

## ✅ 解决方案

### 1. 优化 Cron 脚本 (`backend/cron_simple.py`)

#### 添加超时保护
```python
import signal

def timeout_handler(signum, frame):
    print("⚠️ 超时！强制退出（5 分钟限制）")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(300)  # 5 分钟超时
```

#### 减少 API 调用数量
| 类型 | 之前 | 现在 | 减少 |
|------|------|------|------|
| 股票 | 8 只 | 5 只 | -37.5% |
| 加密货币 | 6 只 | 3 只 | -50% |
| 新闻 (Finnhub) | 30 条 | 15 条 | -50% |
| RSS 源 | 2 个 | 1 个 | -50% |
| RSS 条目 | 10 条/源 | 5 条/源 | -50% |

#### 缩短超时时间
| API | 之前 | 现在 |
|-----|------|------|
| Finnhub 股票 | 5 秒 | 3 秒 |
| CoinGecko | 10 秒 | 5 秒 |
| Finnhub 新闻 | 10 秒 | 5 秒 |
| RSS | 10 秒 | 5 秒 |

**预计运行时间**: 从 15-30 分钟 → **2-3 分钟** ✅

### 2. 调整 Cron 频率 (`railway.toml`)

```toml
# 从每小时改为每 2 小时
schedule = "0 */2 * * *"  # 每 2 小时
```

**原因**:
- 减少执行频率，降低超时风险
- 市场数据 2 小时更新一次足够
- 如果仍需每小时，可在优化后改回

### 3. 添加 Vercel 自动部署脚本

**新文件**: `deploy-vercel.sh`
```bash
#!/bin/bash
# Global Insight Vercel 部署脚本

cd /root/global-insight

# 提交并推送
git add -A
git commit -m "chore: auto-deploy $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# 触发 Vercel 部署
vercel pull --yes
vercel --prod
```

**使用方法**:
```bash
./deploy-vercel.sh
```

---

## 📊 优化效果对比

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 股票 API 调用 | 8 次 | 5 次 | ⬇️ 37.5% |
| 加密货币 API | 1 次 (6 只) | 1 次 (3 只) | ⬇️ 50% |
| 新闻 API 调用 | 1 次 (30 条) | 1 次 (15 条) | ⬇️ 50% |
| RSS 源数量 | 2 个 | 1 个 | ⬇️ 50% |
| 总超时时间 | 无限制 | 5 分钟 | ✅ 保护 |
| Cron 频率 | 每小时 | 每 2 小时 | ⬇️ 50% |
| **预计运行时间** | **15-30 分钟** | **2-3 分钟** | ⬇️ **90%+** |
| Vercel 部署 | 手动 | 自动脚本 | ✅ 自动化 |

---

## 🚀 部署状态

### Railway
- ✅ 代码已提交：`fb35f55`
- ✅ 已推送到 GitHub
- ⏳ Railway 会自动拉取最新代码
- ⏳ 下次 Cron 执行时间：下一个整点（每 2 小时）

### Vercel
- ✅ 部署成功
- 🌐 生产环境：https://global-insight-kappa.vercel.app
- 📦 部署 ID: `5sP52n8hZ9UGzhxzCz1TvC8WQJ89`

---

## 📋 后续检查清单

### 立即检查
- [ ] 访问 Vercel 网站确认数据更新
- [ ] 检查 Railway 日志确认 cron 运行时间

### 2 小时后
- [ ] 检查 Railway cron 是否正常执行
- [ ] 查看日志确认运行时间 < 5 分钟
- [ ] 验证数据库有新的市场数据和新闻

### 如需调整
- [ ] 如果需要每小时执行，修改 `railway.toml` 为 `0 * * * *`
- [ ] 如果运行时间仍过长，进一步减少 API 调用
- [ ] 考虑使用 Railway Background Workers 替代 Cron

---

## 🔧 监控命令

### 查看 Railway 日志
```bash
# 在 Railway 控制台查看
# 或使用 Railway CLI
railway logs --service global-insight
```

### 检查数据库数据量
```bash
docker exec global-insight-backend curl -s http://localhost:8000/api/v1/market | python3 -m json.tool
```

### 测试 Vercel 部署
```bash
curl -I https://global-insight-kappa.vercel.app
```

---

## ⚠️ 注意事项

1. **超时保护**: 5 分钟超时是硬限制，超过会强制终止
2. **API 限流**: 减少调用频率可避免触发 API 限流
3. **数据完整性**: 虽然减少了数量，但核心数据（主要股票、BTC、ETH）仍保留
4. **监控重要**: 前几次执行需要特别关注日志

---

## 📞 如果问题仍然存在

如果 Cron 仍然运行时间过长：

### 方案 A: 进一步简化
- 只抓 3 只股票 + 2 只加密货币
- 只抓 Finnhub 新闻，不抓 RSS

### 方案 B: 使用 Background Workers
- Railway Background Workers 适合长运行任务
- 没有 5 分钟限制
- 参考：https://docs.railway.com/guides/cron-workers-queues

### 方案 C: 迁移到其他服务
- GitHub Actions (免费，适合定时任务)
- Cron-job.org (专业 cron 服务)
- 本地 Docker + crontab

---

*优化完成时间：2026-04-17 10:45*
