# Cron 任务最终配置

**日期**: 2026-04-17  
**状态**: ✅ 完全恢复 + 超时保护

---

## 📊 完整数据配置

### 股票（8 只）✅
```python
symbols = [
    "AAPL",   # Apple
    "TSLA",   # Tesla
    "NVDA",   # NVIDIA
    "GOOGL",  # Google
    "MSFT",   # Microsoft
    "AMD",    # AMD
    "META",   # Meta
    "AMZN"    # Amazon
]
```
- **超时**: 5 秒/只
- **API**: Finnhub

### 加密货币（6 只）✅
```python
crypto_map = {
    "bitcoin": "BTC",      # Bitcoin
    "ethereum": "ETH",     # Ethereum
    "cardano": "ADA",      # Cardano
    "dogecoin": "DOGE",    # Dogecoin
    "solana": "SOL",       # Solana
    "tether": "USDT"       # Tether
}
```
- **超时**: 10 秒
- **API**: CoinGecko

### 新闻（50 条）✅
| 来源 | 数量 | 超时 |
|------|------|------|
| Finnhub API | 30 条 | 10 秒 |
| 中国新闻网财经 | 10 条 | 10 秒 |
| Bloomberg Markets | 10 条 | 10 秒 |
| **总计** | **50 条** | - |

---

## 🛡️ 保留的优化

### 1. 超时保护
```python
import signal

def timeout_handler(signum, frame):
    print("⚠️ 超时！强制退出（5 分钟限制）")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(300)  # 5 分钟超时
```

### 2. 详细日志
- 记录每个 API 的响应状态码
- 记录返回数据条数
- 记录数据库插入条数
- 记录执行时间

### 3. Cron 频率
```toml
# railway.toml
schedule = "0 */2 * * *"  # 每 2 小时
```

---

## 📈 数据总量

| 类型 | 数量 |
|------|------|
| 股票 | 8 只 |
| 加密货币 | 6 只 |
| 黄金 | 1 只 (XAU) |
| 石油 | 2 只 (BRENT, WTI) |
| 新闻 | 50 条/次 |
| **市场数据总计** | **17 只/次** |
| **新闻总计** | **50 条/次** |

---

## ⏱️ 预计运行时间

**5-10 分钟**

分解：
- 股票数据：8 只 × 5 秒 = ~40 秒
- 加密货币：10 秒
- 黄金/石油：~20 秒
- Finnhub 新闻：~2-3 分钟
- RSS 新闻：~2-3 分钟
- 数据库写入：~1 分钟

**安全边际**: 5 分钟超时保护

---

## 🚀 部署状态

- ✅ Git 提交：`ba97949`
- ✅ 已推送 GitHub
- ✅ Vercel 部署完成
- 🌐 https://global-insight-kappa.vercel.app

---

## 📝 日志输出示例

```
==================================================
🕐 Cron 任务开始 - 2026-04-17 10:00:00
==================================================

[10:00:00] 开始抓取市场数据...
  ✅ 市场数据：17 条

[10:01:00] 开始抓取新闻...
  📡 请求 Finnhub API...
  Finnhub 响应状态码：200
  Finnhub 返回数据：30 条
  Finnhub 插入了 30 条
  ✅ 新闻：50 条

==================================================
✅ 完成！市场数据 17 条，新闻 50 条
==================================================
```

---

## 🔍 监控方法

### Railway 日志
```bash
# Railway 控制台
Project → global-insight → Deployments → Logs
```

### 验证数据
```bash
# 检查最新数据时间
docker exec global-insight-backend psql $DATABASE_URL -c \
  "SELECT symbol, type, timestamp FROM market_data 
   ORDER BY timestamp DESC LIMIT 10;"
```

---

## ⚠️ 如果超时

如果运行时间超过 5 分钟：

### 方案 A: 减少新闻数量
```python
# Finnhub 从 30 条减到 20 条
for item in data[:20]:
```

### 方案 B: 延长超时
```python
signal.alarm(600)  # 10 分钟超时
```

### 方案 C: 降低频率
```toml
# railway.toml
schedule = "0 */3 * * *"  # 每 3 小时
```

---

*最终更新时间：2026-04-17 10:49*
