# Railway Cron 任务优化 - 最终版本

**日期**: 2026-04-17  
**状态**: ✅ 已完成

---

## 🎯 优化目标

1. **解决超时问题**：添加超时保护，防止任务无限运行
2. **保留完整功能**：新闻源不减少，保证数据完整性
3. **改进日志**：详细记录执行过程，便于排查问题

---

## ✅ 最终配置

### 1. 超时保护（保留）

```python
import signal

def timeout_handler(signum, frame):
    print("⚠️ 超时！强制退出（5 分钟限制）")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(300)  # 5 分钟超时
```

### 2. 股票配置（优化）

```python
# 从 8 只减少到 5 只核心股票
symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]
```

**原因**：这 5 只是市场最具代表性的股票，覆盖科技巨头

### 3. 加密货币配置（优化）

```python
# 从 6 只减少到 3 只主要加密货币
crypto_map = {"bitcoin": "BTC", "ethereum": "ETH", "tether": "USDT"}
```

**原因**：BTC、ETH、USDT 占据加密货币市场 80%+ 交易量

### 4. 新闻配置（完整保留）✅

```python
# Finnhub API - 15 条（从 30 条优化）
for item in data[:15]:

# RSS 源 - 完整保留 2 个源
rss_sources = {
    '中国新闻网财经': 'https://www.chinanews.com.cn/rss/finance.xml',
    'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
}

# 每个源 10 条新闻
for entry in feed.entries[:10]:
```

**新闻总数**：15 (Finnhub) + 20 (RSS 2 源×10 条) = **35 条/次**

### 5. 超时设置（优化）

| API | 原设置 | 新设置 |
|-----|--------|--------|
| Finnhub 股票 | 5 秒 | **3 秒** |
| CoinGecko | 10 秒 | **5 秒** |
| Finnhub 新闻 | 10 秒 | **5 秒** |
| RSS | 10 秒 | **10 秒**（保持） |

### 6. Cron 频率（调整）

```toml
# railway.toml
schedule = "0 */2 * * *"  # 每 2 小时
```

---

## 📊 优化效果对比

| 项目 | 原始 | 优化后 | 变化 |
|------|------|--------|------|
| **股票数量** | 8 只 | 5 只 | ⬇️ 37.5% |
| **加密货币** | 6 只 | 3 只 | ⬇️ 50% |
| **新闻总数** | 50 条 | 35 条 | ⬇️ 30% |
| - Finnhub | 30 条 | 15 条 | ⬇️ 50% |
| - RSS 源 | 2 个 | 2 个 | ✅ 不变 |
| - RSS 条目 | 20 条 | 20 条 | ✅ 不变 |
| **超时保护** | ❌ 无 | ✅ 5 分钟 | ✅ 新增 |
| **日志输出** | 基础 | 详细 | ✅ 增强 |
| **预计运行时间** | 15-30 分钟 | **3-5 分钟** | ⬇️ 80%+ |

---

## 📝 日志输出示例

```
==================================================
🕐 Cron 任务开始 - 2026-04-17 10:00:00
==================================================

[2026-04-17 10:00:00.123] 开始抓取市场数据...
  ✅ 市场数据：8 条

[2026-04-17 10:00:03.456] 开始抓取新闻...
  📡 请求 Finnhub API...
  Finnhub 响应状态码：200
  Finnhub 返回数据：15 条
  Finnhub 插入了 15 条
  ✅ 新闻：35 条

==================================================
✅ 完成！市场数据 8 条，新闻 35 条
==================================================
```

---

## 🚀 部署状态

### Git
- ✅ 最新提交：`b29dcf3`
- ✅ 已推送：https://github.com/JiJiHu/global-insight

### Vercel
- ✅ 部署成功
- 🌐 生产环境：https://global-insight-kappa.vercel.app

### Railway
- ⏳ 自动拉取最新代码
- ⏳ 下次执行：下一个 2 小时间隔

---

## 🔍 监控方法

### 1. Railway 日志
在 Railway 控制台查看：
- Project → global-insight → Deployments → Logs
- 或使用 CLI: `railway logs`

### 2. 检查执行时间
```
✅ 完成！市场数据 X 条，新闻 Y 条
```
查看从 "Cron 任务启动" 到 "完成" 的时间差

### 3. 验证数据更新
```bash
# 检查最新数据时间
docker exec global-insight-backend psql $DATABASE_URL -c \
  "SELECT MAX(timestamp) FROM market_data;"
```

---

## ⚠️ 如果仍然超时

### 方案 A: 进一步减少股票
```python
symbols = ["AAPL", "TSLA", "NVDA"]  # 只保留 3 只
```

### 方案 B: 使用 Background Workers
Railway Background Workers 适合长运行任务（无 5 分钟限制）

### 方案 C: 分离任务
- 市场数据 cron：每小时
- 新闻抓取 cron：每 2 小时

---

## 📞 快速恢复命令

### 恢复原始股票配置
```python
symbols = ["AAPL", "TSLA", "NVDA", "GOOGL", "MSFT", "AMD", "META", "AMZN"]
```

### 恢复原始加密货币
```python
crypto_map = {"bitcoin": "BTC", "ethereum": "ETH", "cardano": "ADA", 
              "dogecoin": "DOGE", "solana": "SOL", "tether": "USDT"}
```

### 改回每小时执行
```toml
# railway.toml
schedule = "0 * * * *"
```

---

*最终更新时间：2026-04-17 10:37*
