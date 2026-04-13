# 📈 Finance Insight Dashboard

金融数据 + 新闻聚合 + AI 关联分析平台

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────┐
│                   Vercel (前端)                          │
│              Next.js + Recharts + shadcn/ui             │
└─────────────────────┬───────────────────────────────────┘
                      │ fetch()
┌─────────────────────▼───────────────────────────────────┐
│              服务器 (FastAPI 后端)                        │
│         /api/v1/market  /api/v1/news  /api/v1/insight   │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│          PostgreSQL + pgvector (数据库)                  │
│    market_data  |  news (embedding)  |  insights        │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
/root/finance-dashboard/
├── docker-compose.yml          # PostgreSQL 容器配置
├── README.md                   # 本文档
└── backend/
    ├── requirements.txt        # Python 依赖
    ├── config.py              # 配置文件
    ├── db.py                  # 数据库连接
    ├── fetch_market_data.py   # 金融数据抓取
    ├── vectorize_news.py      # 新闻向量化
    ├── api.py                 # FastAPI 服务
    ├── run_pipeline.py        # 主运行脚本
    └── install.sh             # 安装脚本
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /root/finance-dashboard/backend
bash install.sh
source venv/bin/activate
```

### 2. 配置 API Key

编辑 `config.py`:
```python
ALPHA_VANTAGE_API_KEY = "你的 API Key"  # 注册：https://www.alphavantage.co/support/#api-key
```

### 3. 测试运行

```bash
# 测试数据库连接
python db.py

# 抓取金融数据
python fetch_market_data.py

# 测试向量化
python vectorize_news.py

# 启动 API 服务
python api.py
```

访问 http://localhost:8000/docs 查看 API 文档

---

## ⏰ 定时任务

编辑 crontab:
```bash
crontab -e
```

添加:
```bash
# 每 5 分钟抓取金融数据
*/5 * * * * cd /root/finance-dashboard/backend && ./venv/bin/python fetch_market_data.py >> /var/log/finance-market.log 2>&1

# 每小时抓取新闻并向量化
0 * * * * cd /root/finance-dashboard/backend && ./venv/bin/python run_pipeline.py >> /var/log/finance-pipeline.log 2>&1
```

---

## 📊 数据库表

### market_data
| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| symbol | VARCHAR(20) | 标的代码 |
| type | VARCHAR(20) | 类型 (stock/commodity/forex) |
| price | DECIMAL | 价格 |
| change_percent | DECIMAL | 涨跌幅 |
| volume | BIGINT | 成交量 |
| timestamp | TIMESTAMPTZ | 时间戳 |

### news
| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| title | TEXT | 标题 |
| content | TEXT | 内容 |
| source | VARCHAR(50) | 来源 |
| embedding | vector(768) | 向量嵌入 |
| sentiment_score | DECIMAL | 情感分数 (-1~1) |
| related_symbols | TEXT[] | 相关标的 |

---

## 🔧 运维

### 查看容器状态
```bash
docker ps | grep finance-db
```

### 查看日志
```bash
docker logs finance-db
```

### 备份数据库
```bash
docker exec finance-db pg_dump -U jack finance_insight > backup.sql
```

### 恢复数据库
```bash
docker exec -i finance-db psql -U jack finance_insight < backup.sql
```

---

## 📝 待办事项

- [ ] 集成 OpenClaw 新闻抓取技能
- [ ] 实现关联分析算法
- [ ] 开发 Vercel 前端
- [ ] 添加用户认证
- [ ] 配置监控告警

---

*Powered by PostgreSQL + pgvector + FastAPI*
