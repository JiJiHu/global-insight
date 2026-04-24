# 新闻栏显示问题修复总结

## 问题描述
- 前端有些新闻栏为空
- 有的新闻栏没有专门的列表

## 根本原因
前端硬编码的新闻源名称与数据库实际存储的新闻源名称不匹配：

**前端硬编码的源名称** | **数据库实际源名称** | **匹配状态**
---|---|---
央视网 | ❌ 不存在 | ❌ 不匹配
投资快报 | ❌ 不存在 | ❌ 不匹配
中国新闻网财经 | ✅ 中国新闻网财经 | ✅ 匹配
Finnhub | ✅ Finnhub | ✅ 匹配
Twitter | ✅ Twitter-* | ✅ 模糊匹配
Bloomberg | ✅ Bloomberg Markets | ✅ 模糊匹配
Reuters | ✅ Reuters - Google News | ✅ 模糊匹配

## 修复内容

### 1. 更新前端新闻源按钮
文件：`/root/global-insight/frontend/index.html`

**修改前：**
```html
<button :class="{ active: newsSource === '央视网' }" @click="newsSource = '央视网'">央视网</button>
<button :class="{ active: newsSource === '投资快报' }" @click="newsSource = '投资快报'">投资快报</button>
```

**修改后：**
```html
<button :class="{ active: newsSource === '中国新闻网财经' }" @click="newsSource = '中国新闻网财经'">中新网财经</button>
<button :class="{ active: newsSource === 'Investing' }" @click="newsSource = 'Investing'">Investing.com</button>
```

### 2. 新闻源对应关系

**前端按钮** | **数据库匹配模式** | **新闻数量**
---|---|---
全部 | 全部 | ~2200 条
Finnhub | `source LIKE 'Finnhub%'` | ~1639 条
Twitter/X | `source LIKE 'Twitter%'` | ~32 条
中新网财经 | `source = '中国新闻网财经'` | ~114 条
Bloomberg | `source LIKE 'Bloomberg%'` | ~173 条
CNBC | `source LIKE 'CNBC%'` | ~123 条
Reuters | `source LIKE 'Reuters%'` | ~33 条
Investing.com | `source LIKE 'Investing%'` | ~387 条
GitHub | `source = 'GitHub'` | ~20 条

### 3. 过滤逻辑（无需修改）
前端已有模糊匹配逻辑：
```javascript
const filteredNewsList = computed(() => {
    if (newsSource.value === 'all') {
        return newsList.value;
    }
    return newsList.value.filter(item => {
        if (!item.source) return false;
        const source = item.source.toLowerCase();
        const target = newsSource.value.toLowerCase();
        return source.includes(target);  // 模糊匹配
    });
});
```

## 验证步骤

### 1. 查看数据库新闻源
```bash
docker exec global-insight-backend python3 -c "
from db import get_db_connection
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute('SELECT source, COUNT(*) FROM news GROUP BY source ORDER BY COUNT(*) DESC')
    for row in cur.fetchall():
        print(f'{row[0]:30} {row[1]:5}')
"
```

### 2. 访问前端
打开浏览器访问：http://150.40.177.181:11279

### 3. 测试新闻筛选
- 点击"全部" → 显示所有新闻
- 点击"中新网财经" → 显示 ~114 条中国新闻
- 点击"Twitter/X" → 显示 ~32 条推文
- 点击"CNBC" → 显示 ~123 条 CNBC 新闻

## 定时抓取任务

已配置每 12 小时自动抓取（06:00 和 18:00）：
```bash
0 6,18 * * * docker exec global-insight-backend python3 /app/fetch_news_sources.py
```

抓取内容：
- ✅ 中国新闻网财经 RSS
- ✅ Twitter 财经新闻（Reuters, Bloomberg, CNBC, WSJ, FinancialTimes）

## 后续优化建议

1. **动态生成新闻源按钮** - 从 API 获取实际存在的新闻源，自动生成按钮
2. **添加更多国内新闻源** - 央视网财经、经济参考报、第一财经
3. **优化 Twitter 时间戳** - 研究获取推文实际发布时间的方法

---

修复时间：2026-04-03 20:11
修复状态：✅ 已完成
