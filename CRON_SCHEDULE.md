# Global Insight 数据源获取频率

## 📊 总览

| 数据类型 | 频率 | 来源数 | 日均请求 |
|----------|------|--------|----------|
| 市场数据 | 每小时 | 2 | 48 次/天 |
| 新闻数据 | 每 12 小时 | 4 | 2 次/天 |
| AI 洞察 | 每 12 小时 | 1 | 2 次/天 |

---

## 📈 市场数据（每小时）

### 1. 美股/加密货币数据
- **频率**: 每小时
- **脚本**: `fetch_market_data.py`
- **Cron**: `0 * * * *`
- **数据源**: 
  - 股票：AAPL, TSLA, NVDA, GOOGL, MSFT, AMD, META, AMZN
  - 加密货币：BTC, ETH, ADA, DOGE, SOL, USDT
- **API**: Finnhub

### 2. 大宗商品数据
- **频率**: 每小时
- **脚本**: `fetch_commodities.py`
- **Cron**: `0 * * * *`
- **数据源**:
  - 黄金：XAU
  - 石油：BRENT, WTI
- **API**: Finnhub + 其他

---

## 📰 新闻数据（每 12 小时）

### 1. 多源新闻
- **频率**: 每 12 小时 (06:00, 18:00)
- **脚本**: `fetch_news_sources.py`
- **Cron**: `0 6,18 * * *`
- **来源**:
  - 中国新闻网财经 RSS
  - Twitter: Reuters, Bloomberg, CNBC, WSJ, FinancialTimes
- **数量**: ~2426 条

---

## 🤖 AI 洞察（每 12 小时）

### 1. AI 洞察生成
- **频率**: 每 12 小时 (07:00, 19:00)
- **脚本**: `generate_ai_insights_v3.py`
- **Cron**: `0 7,19 * * *`
- **输入**: 市场数据 + 新闻数据
- **输出**: AI 洞察分析

---

## 📋 完整 Crontab

```bash
# 市场数据 - 每小时
0 * * * * docker exec global-insight-backend python3 /app/fetch_market_data.py
0 * * * * docker exec global-insight-backend python3 /app/fetch_commodities.py

# 新闻数据 - 每 12 小时
0 6,18 * * * docker exec global-insight-backend python3 /app/fetch_news_sources.py

# AI 洞察 - 每 12 小时
0 7,19 * * * docker exec global-insight-backend python3 /app/generate_ai_insights_v3.py
```

---

## 📊 当前数据量

| 新闻源 | 数量 | 更新频率 |
|--------|------|----------|
| Finnhub | 1639 | 每 12 小时 |
| Investing.com | 397 | 每 12 小时 |
| 中国新闻网财经 | 117 | 每 12 小时 |
| Bloomberg | 104 | 每 12 小时 |
| CNBC | 82 | 每 12 小时 |
| Reuters | 41 | 每 12 小时 |
| GitHub | 30 | 静态 |
| Twitter | 25 | 每 12 小时 |

**总计**: 2426 条新闻

---

## 🔔 下次抓取时间

- **市场数据**: 下一个整点
- **新闻数据**: 今日 18:00
- **AI 洞察**: 今日 19:00

---

最后更新：2026-04-03 20:47
