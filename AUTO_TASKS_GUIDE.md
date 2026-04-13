# Global Insight 自动任务配置指南

**配置时间**: 2026-03-11  
**配置文件**: `/root/finance-dashboard/cron_jobs.sh`  
**日志目录**: `/var/log/finance/`

---

## 📋 任务清单

### 1. 数据刷新任务

| 任务 | 频率 | 时间 | 说明 |
|------|------|------|------|
| **大宗商品数据** | 每 10 分钟 | */10 * * * * | 黄金、石油、加密货币实时价格 |
| **RSS 新闻** | 每 30 分钟 | */30 * * * * | CNBC/Reuters/Bloomberg 等 RSS 订阅 |
| **AI 洞察** | 每小时 | 0 * * * * | 生成市场总结、新闻提醒、行业分析 |
| **知识图谱** | 每天 1 次 | 0 6 * * * | 重建节点关系图谱 |

**数据流向**:
```
外部 API → fetch_*.py → PostgreSQL → API → 前端展示
```

---

### 2. 系统维护任务

| 任务 | 频率 | 时间 | 说明 |
|------|------|------|------|
| **浏览器重启** | 每天 1 次 | 0 3 * * * | 清理僵尸进程，释放内存 |
| **清理僵尸进程** | 每天 1 次 | 0 4 * * * | 清理超 24 小时的 Chrome 进程 |
| **健康报告** | 每天 1 次 | 0 7 * * * | 生成系统状态报告 |

---

## 📂 文件结构

```
/root/finance-dashboard/
├── cron_jobs.sh                    # 主配置脚本
├── backend/
│   ├── fetch_commodities.py        # 大宗商品获取
│   ├── fetch_rss_news.py           # RSS 新闻获取
│   ├── generate_insights_v2.py     # AI 洞察生成
│   └── build_knowledge_graph_v2.py # 知识图谱构建
├── scripts/
│   ├── restart_browser.sh          # 浏览器重启
│   ├── cleanup_zombies.sh          # 清理僵尸进程
│   └── health_report.sh            # 健康报告
└── logs/
    └── /var/log/finance/           # 日志目录
        ├── commodities.log
        ├── rss_news.log
        ├── insights.log
        ├── graph.log
        ├── browser.log
        ├── cleanup.log
        └── health_*.md
```

---

## 🔧 管理命令

### 查看任务
```bash
# 查看所有 crontab 任务
crontab -l

# 查看 Global Insight 相关任务
crontab -l | grep finance
```

### 编辑任务
```bash
# 编辑 crontab
crontab -e

# 添加新任务（示例）
*/5 * * * * docker exec finance-backend python3 /app/fetch_commodities.py >> /var/log/finance/commodities.log 2>&1
```

### 删除任务
```bash
# 删除所有任务（谨慎！）
crontab -r

# 删除特定任务
crontab -l | grep -v "fetch_commodities" | crontab -
```

### 查看日志
```bash
# 实时查看日志
tail -f /var/log/finance/commodities.log
tail -f /var/log/finance/rss_news.log
tail -f /var/log/finance/insights.log

# 查看最新 100 行
tail -n 100 /var/log/finance/insights.log

# 查看今天的日志
cat /var/log/finance/health_$(date +%Y%m%d).md
```

### 手动执行
```bash
# 手动刷新数据
docker exec finance-backend python3 /app/fetch_commodities.py
docker exec finance-backend python3 /app/fetch_rss_news.py
docker exec finance-backend python3 /app/generate_insights_v2.py
docker exec finance-backend python3 /app/build_knowledge_graph_v2.py

# 手动重启浏览器
/root/finance-dashboard/scripts/restart_browser.sh

# 手动清理僵尸进程
/root/finance-dashboard/scripts/cleanup_zombies.sh

# 手动生成健康报告
/root/finance-dashboard/scripts/health_report.sh
```

---

## 📊 监控与告警

### 检查任务状态
```bash
# 检查 crontab 服务
systemctl status cron

# 查看任务执行历史
grep CRON /var/log/syslog | tail -20
```

### 检查数据新鲜度
```bash
# 检查最新数据时间
curl -s http://localhost:11279/api/v1/stats | python3 -m json.tool

# 检查知识图谱
curl -s http://localhost:11279/api/v1/graph | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'节点：{len(d[\"nodes\"])}, 边：{len(d[\"links\"])}')"
```

### 检查浏览器状态
```bash
# 检查 CDP 端口
curl -s http://127.0.0.1:18800/json/version | grep Browser

# 检查僵尸进程
ps aux | grep "chrome.*defunct" | wc -l
```

---

## ⚠️ 故障排查

### 问题 1：数据未更新
**症状**: 前端显示旧数据

**排查步骤**:
1. 检查任务是否执行
   ```bash
   tail -n 20 /var/log/finance/commodities.log
   ```
2. 手动执行脚本
   ```bash
   docker exec finance-backend python3 /app/fetch_commodities.py
   ```
3. 检查 Docker 容器状态
   ```bash
   docker-compose ps
   ```

### 问题 2：浏览器超时
**症状**: 浏览器工具调用失败

**排查步骤**:
1. 检查僵尸进程
   ```bash
   ps aux | grep "chrome.*defunct" | wc -l
   ```
2. 重启浏览器
   ```bash
   /root/finance-dashboard/scripts/restart_browser.sh
   ```
3. 检查 CDP 端口
   ```bash
   curl -s http://127.0.0.1:18800/json/version
   ```

### 问题 3：AI 洞察不更新
**症状**: 洞察数量不变

**排查步骤**:
1. 检查生成脚本
   ```bash
   tail -n 20 /var/log/finance/insights.log
   ```
2. 手动生成
   ```bash
   docker exec finance-backend python3 /app/generate_insights_v2.py
   ```
3. 检查 API
   ```bash
   curl -s http://localhost:11279/api/v1/insights?limit=10
   ```

---

## 📈 性能优化建议

### 1. 调整刷新频率
根据实际需求调整：
- **高频交易**: 大宗商品每 5 分钟
- **一般监控**: 新闻每 1 小时
- **低频数据**: 知识图谱每周 1 次

### 2. 资源限制
为 Docker 容器设置资源限制：
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

### 3. 日志轮转
防止日志文件过大：
```bash
# /etc/logrotate.d/finance
/var/log/finance/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 🎯 最佳实践

### 1. 定期清理
```bash
# 每周清理一次旧日志
0 2 * * 0 find /var/log/finance -name "*.log" -mtime +7 -delete
```

### 2. 健康检查
```bash
# 每小时检查一次服务
0 * * * * curl -f http://localhost:11279/api/v1/health || echo "服务异常" | mail -s "Global Insight 告警" admin@example.com
```

### 3. 备份配置
```bash
# 每天备份 crontab
0 0 * * * crontab -l > /root/finance-dashboard/backup/crontab_$(date +%Y%m%d).txt
```

---

## 📝 更新记录

| 日期 | 更新内容 | 操作 |
|------|----------|------|
| 2026-03-11 | 初始配置 | 配置 7 个自动任务 |
| 2026-03-11 | 添加浏览器维护 | 重启 + 清理僵尸进程 |
| 2026-03-11 | 添加健康报告 | 每天生成状态报告 |

---

## 🆘 紧急联系

如遇到严重问题：
1. 查看健康报告：`/var/log/finance/health_*.md`
2. 检查所有日志：`tail -f /var/log/finance/*.log`
3. 重启所有服务：`docker-compose restart`
4. 重启浏览器：`/root/finance-dashboard/scripts/restart_browser.sh`

---

*最后更新：2026-03-11*  
*维护人员：Biko 🐶*
