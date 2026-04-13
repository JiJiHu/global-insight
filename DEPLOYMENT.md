# 🚀 金融看板部署说明

**部署时间**: 2026-03-07  
**服务器**: 150.40.177.181  
**端口**: 11279

---

## 🌐 访问地址

### 公网访问
```
http://150.40.177.181:11279
```

### 本地访问
```
http://localhost:11279
```

---

## 📊 服务配置

| 服务 | 容器名 | 端口 | 状态 |
|------|--------|------|------|
| **前端** | finance-frontend | 11279 → 80 | ✅ Nginx |
| **后端 API** | finance-backend | 8000 → 8000 | ✅ FastAPI |
| **数据库** | finance-db | 5432 → 5432 | ✅ PostgreSQL |

---

## 🔧 防火墙配置

### 如果无法访问公网，需要在云服务器控制台开放端口：

#### 阿里云
1. 登录阿里云控制台
2. 进入 ECS → 安全组
3. 添加入方向规则：
   - 端口范围：`11279/11279`
   - 授权对象：`0.0.0.0/0`
   - 协议：`TCP`

#### 腾讯云
1. 登录腾讯云控制台
2. 进入 CVM → 安全组
3. 添加入站规则：
   - 端口：`11279`
   - 来源：`0.0.0.0/0`
   - 协议：`TCP`

#### 华为云
1. 登录华为云控制台
2. 进入 ECS → 安全组
3. 添加入方向规则：
   - 端口：`11279`
   - 源地址：`0.0.0.0/0`
   - 协议：`TCP`

#### AWS
1. 登录 AWS 控制台
2. 进入 EC2 → Security Groups
3. 添加入站规则：
   - 端口：`11279`
   - 来源：`0.0.0.0/0`
   - 协议：`TCP`

---

## 🛠️ 运维命令

### 查看服务状态
```bash
docker ps | grep finance
```

### 查看日志
```bash
# 前端日志
docker logs finance-frontend

# 后端日志
docker logs finance-backend

# 数据库日志
docker logs finance-db
```

### 重启服务
```bash
cd /root/finance-dashboard
docker-compose restart
```

### 停止服务
```bash
cd /root/finance-dashboard
docker-compose down
```

### 启动服务
```bash
cd /root/finance-dashboard
docker-compose up -d
```

---

## 📁 项目结构

```
/root/finance-dashboard/
├── docker-compose.yml          # Docker 配置
├── DEPLOYMENT.md               # 本文档
├── TASKS_COMPLETED.md          # 功能完成报告
├── frontend/
│   ├── index.html              # 前端页面（含图谱可视化）
│   ├── Dockerfile              # 前端镜像
│   └── nginx.conf              # Nginx 配置
└── backend/
    ├── api.py                  # FastAPI 服务
    ├── knowledge_graph.py      # 知识图谱生成
    ├── generate_insights.py    # AI 洞察生成
    ├── fetch_market_data.py    # 行情数据抓取
    ├── fetch_news.py           # 新闻抓取
    ├── vectorize_news.py       # 新闻向量化
    ├── db.py                   # 数据库连接
    ├── config.py               # 配置文件
    └── price_alerts.py         # 价格告警
```

---

## ⏰ 定时任务

| 频率 | 任务 | 脚本 |
|------|------|------|
| `*/5 * * * *` | 行情数据抓取 | `cron-job.sh` |
| `0 * * * *` | 新闻抓取 | `cron-news.sh` |
| `*/15 * * * *` | 价格告警检查 | `cron-alerts.sh` |
| `0 */4 * * *` | 知识图谱生成 | `cron-graph.sh` |
| `0 */4 * * *` | AI 洞察生成 | `cron-insights.sh` |

查看定时任务：
```bash
crontab -l | grep finance
```

---

## 🔍 API 接口

### 基础 URL
```
http://150.40.177.181:11279/api/v1
```

### 可用接口

| 接口 | 说明 | 示例 |
|------|------|------|
| `GET /health` | 健康检查 | `/api/v1/health` |
| `GET /market` | 行情数据 | `/api/v1/market` |
| `GET /news` | 新闻列表 | `/api/v1/news?limit=20` |
| `GET /insights` | AI 洞察 | `/api/v1/insights?limit=10` |
| `GET /graph` | 知识图谱 | `/api/v1/graph` |
| `GET /stats` | 数据统计 | `/api/v1/stats` |

API 文档：http://150.40.177.181:11279/docs

---

## 📊 当前数据状态

- **行情数据**: 2,849 条
- **新闻数据**: 753 条
- **AI 洞察**: 29 条
- **知识图谱**: 78 节点 / 46 边

---

## 🎯 功能特性

### ✅ 已实现
1. **实时行情监控** - 每 5 分钟更新
2. **新闻自动抓取** - 每小时更新，带情感分析
3. **AI 关联分析** - 情感 - 价格关联、市场总结
4. **知识图谱** - 股票 - 新闻关联网络可视化
5. **价格告警** - 涨跌幅超过 5% 触发
6. **交互式前端** - ECharts 力导向图、实时数据展示

### 🚧 待完成
1. 告警通知推送（WhatsApp/飞书）
2. 移动端响应式优化
3. 更多数据源接入
4. 日报/周报自动生成

---

## 💡 使用建议

1. **首次访问**: 打开 http://150.40.177.181:11279 查看仪表盘
2. **查看图谱**: 滚动到页面底部，查看知识图谱可视化
3. **交互操作**:
   - 鼠标悬停节点查看详情
   - 拖拽节点调整位置
   - 滚轮缩放
   - 点击布局切换按钮
4. **数据刷新**: 每 5 分钟自动刷新，也可点击右下角刷新按钮

---

*最后更新：2026-03-07 17:00*
