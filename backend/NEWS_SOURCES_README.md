# Global Insight 新闻源说明

## 实时性说明

### ✅ 完全实时新闻源

| 新闻源 | 类型 | 更新频率 | 时间戳 |
|--------|------|----------|--------|
| **Finnhub** | API | 实时推送 | 新闻实际发布时间 |
| **中国新闻网财经** | RSS | 每小时抓取 | RSS 中的发布时间 |

### ⚠️ 半实时新闻源

| 新闻源 | 类型 | 更新频率 | 时间戳 |
|--------|------|----------|--------|
| **Twitter** | Jina AI | 每小时抓取 | 抓取时间（非推文发布时间） |

**Twitter 局限性说明：**
- Jina AI 返回的 Twitter 内容不包含每条推文的具体发布时间
- 当前使用抓取时间作为 `created_at`
- 这是技术限制，不影响新闻内容本身

## 当前配置

### RSS 源
```python
'中国新闻网财经': {
    'type': 'rss',
    'url': 'https://www.chinanews.com.cn/rss/finance.xml',
    'enabled': True
}
```

### Twitter 账号
```python
'Twitter 财经': {
    'type': 'twitter',
    'accounts': ['Reuters', 'Bloomberg', 'CNBC', 'WSJ', 'FinancialTimes'],
    'enabled': True
}
```

## 使用方法

### 手动执行
```bash
docker exec global-insight-backend python3 /app/fetch_news_sources.py
```

### 定时任务（每小时）
```bash
# 添加到 crontab
0 * * * * docker exec global-insight-backend python3 /app/fetch_news_sources.py >> /var/log/news_fetch.log 2>&1
```

## 数据验证

### 查看最新新闻
```bash
docker exec global-insight-backend python3 -c "
import sys
sys.path.insert(0, '/app')
from db import get_db_connection
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute('SELECT title, source, created_at FROM news ORDER BY created_at DESC LIMIT 10')
    for row in cur.fetchall():
        print(f'{row[1]:25} {row[2]} - {row[0][:50]}')
"
```

### 查看新闻源分布
```bash
docker exec global-insight-backend python3 -c "
import sys
sys.path.insert(0, '/app')
from db import get_db_connection
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute('SELECT source, COUNT(*) FROM news GROUP BY source ORDER BY COUNT(*) DESC')
    for row in cur.fetchall():
        print(f'{row[0]:25} {row[1]:5}')
"
```

## 未来改进

1. **Twitter 时间戳优化**：研究其他 API（如 snscrape）获取推文实际发布时间
2. **更多国内新闻源**：央视网财经、经济参考报、第一财经（需要网页解析）
3. **去重优化**：基于内容相似度去重，避免重复新闻

---

最后更新：2026-04-03
