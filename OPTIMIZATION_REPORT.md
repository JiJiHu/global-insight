# Global Insight 项目优化报告

**检查时间**: 2026-04-03 20:50  
**检查人**: Biko 🐶

---

## 📊 项目概览

| 指标 | 数值 | 状态 |
|------|------|------|
| 项目大小 | 5.5 GB | ⚠️ 较大 (venv 占 5.5G) |
| Python 脚本 | 46 个 | ⚠️ 重复较多 |
| 前端文件 | 1 个 (1117 行) | ✅ 简洁 |
| 数据库表 | 4 个 | ✅ 合理 |
| 新闻总数 | 2426 条 | ✅ 正常 |

---

## 🔴 高优先级优化

### 1. 清理重复脚本

**问题**: 存在大量功能重复的脚本

| 功能 | 重复脚本 | 建议 |
|------|----------|------|
| 新闻抓取 | `fetch_news.py`, `fetch_news_simple.py`, `fetch_news_minimal.py`, `fetch_more_news.py`, `fetch_realtime_news.py`, `fetch_rss_news.py`, `fetch_top_news.py`, `fetch_social_news.py`, `fetch_twitter_news.py` | 合并为 1-2 个 |
| 洞察生成 | `generate_insights.py`, `generate_insights_v2.py`, `generate_ai_insights_v3.py`, `generate_realtime_insights.py` | 保留最新版 |
| 新闻添加 | `add_news_sources.py`, `add_more_news_sources.py`, `add_news_content.py` | 合并或归档 |

**建议操作**:
```bash
# 1. 归档旧脚本
mkdir -p /root/global-insight/backend/archive
mv /root/global-insight/backend/fetch_news.py /root/global-insight/backend/archive/
mv /root/global-insight/backend/fetch_news_simple.py /root/global-insight/backend/archive/
mv /root/global-insight/backend/generate_insights.py /root/global-insight/backend/archive/
mv /root/global-insight/backend/generate_insights_v2.py /root/global-insight/backend/archive/

# 2. 更新 crontab 使用新脚本
```

---

### 2. 数据库查询优化

**问题**: API 使用 `SELECT *` 查询所有字段

**当前代码** (`api.py`):
```python
cur.execute("""
    SELECT id, title, content, source, sentiment_label, created_at, url
    FROM news
    ORDER BY created_at DESC
    LIMIT %s
""", (limit,))
```

**优化建议**:
1. ✅ 已明确指定字段（未使用 SELECT *）
2. ⚠️ 缺少分页支持（只有 LIMIT，无 OFFSET）
3. ⚠️ 缺少缓存机制

**建议添加**:
```python
# 添加分页支持
@app.get("/api/v1/news")
def get_news(limit: int = 50, offset: int = 0):
    # ...

# 添加 Redis 缓存
from functools import lru_cache
@lru_cache(maxsize=100)
def get_cached_news(limit: int):
    # ...
```

---

### 3. 数据库索引优化

**现有索引**: ✅ 良好
- `news.idx_news_created_at` - 时间排序
- `news.idx_news_sentiment` - 情感筛选
- `news.idx_news_symbols` - 关联查询
- `market_data.idx_market_symbol_timestamp` - 时间序列

**建议添加**:
```sql
-- 新闻来源筛选
CREATE INDEX idx_news_source ON news(source);

-- 复合索引（常用查询）
CREATE INDEX idx_news_source_created ON news(source, created_at DESC);
```

---

### 4. 前端性能优化

**问题**: 单文件 1117 行，包含所有逻辑

**建议**:
1. **拆分组件**: 将新闻列表、图表、统计拆分为独立组件
2. **懒加载**: 新闻数据分页加载，避免一次加载 500 条
3. **缓存优化**: 添加浏览器缓存策略

**当前问题**:
```javascript
// 一次加载 500 条新闻
const res = await fetch(`${API_BASE}/news?limit=500`);
```

**优化建议**:
```javascript
// 分页加载
const loadNews = async (page = 1) => {
  const res = await fetch(`${API_BASE}/news?limit=50&offset=${(page-1)*50}`);
  // ...
}
```

---

## 🟡 中优先级优化

### 5. Docker 配置优化

**当前配置**:
```yaml
postgres:
  deploy:
    resources:
      limits:
        memory: 512M  # ⚠️ 可能不足
```

**建议**:
```yaml
postgres:
  deploy:
    resources:
      limits:
        memory: 1G    # ✅ 增加到 1G
        cpus: '1.0'
      reservations:
        memory: 256M
        cpus: '0.5'
```

---

### 6. 日志管理

**问题**: 日志文件可能无限增长

**建议添加日志轮转**:
```bash
# /etc/logrotate.d/global-insight
/var/log/global-insight/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

---

### 7. 错误处理增强

**当前问题**: 部分脚本缺少错误处理

**示例** (`fetch_news_sources.py`):
```python
try:
    response = requests.get(url, timeout=30)
except Exception as e:
    print(f"❌ 失败：{e}")  # ⚠️ 只打印，未重试
```

**建议**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_with_retry(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response
```

---

## 🟢 低优先级优化

### 8. 代码规范

**问题**: 缺少统一的代码风格

**建议**:
```bash
# 安装工具
pip install black flake8 mypy

# 格式化代码
black /root/global-insight/backend/*.py

# 代码检查
flake8 /root/global-insight/backend/
```

---

### 9. 监控告警

**建议添加**:
1. **健康检查端点**: `/api/v1/health`
2. **监控指标**: API 响应时间、数据库连接数
3. **告警规则**: 
   - API 错误率 > 5%
   - 数据更新延迟 > 2 小时
   - 磁盘使用率 > 80%

---

### 10. 安全性增强

**当前问题**:
- ⚠️ 数据库密码硬编码
- ⚠️ API 无认证
- ⚠️ 无 HTTPS

**建议**:
1. 使用环境变量存储敏感信息
2. 添加 API Token 认证
3. 配置 Nginx SSL

---

## 📋 优化行动计划

### 第一阶段（本周）
- [ ] 归档重复脚本
- [ ] 添加数据库索引
- [ ] 配置日志轮转

### 第二阶段（下周）
- [ ] 前端分页加载
- [ ] 增强错误处理
- [ ] 添加监控告警

### 第三阶段（下月）
- [ ] API 认证机制
- [ ] Docker 资源优化
- [ ] 代码规范化

---

## 📊 预期收益

| 优化项 | 预期收益 | 难度 |
|--------|----------|------|
| 清理重复脚本 | 减少 50% 代码量 | ⭐ |
| 数据库索引 | 查询速度提升 10 倍 | ⭐ |
| 前端分页 | 加载速度提升 5 倍 | ⭐⭐ |
| 错误处理 | 系统稳定性提升 | ⭐⭐ |
| 监控告警 | 问题发现时间缩短 | ⭐⭐⭐ |

---

**总结**: 项目整体架构良好，主要问题是脚本重复和缺少一些工程化实践。按优先级逐步优化即可。
