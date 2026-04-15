# Railway Cron 完整配置指南

**最后更新**: 2026-04-14 15:19  
**项目**: zestful-education  
**服务**: efficient-creativity (Cron 服务)

---

## 📋 完整配置步骤

### 步骤 1: 确认服务已创建

访问项目页面：
```
https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f
```

**确认**：
- ✅ efficient-creativity 服务存在
- ✅ 服务状态正常

---

### 步骤 2: 配置环境变量

访问：
```
https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/variables
```

**添加以下变量**：

| Variable Name | Variable Value | 说明 |
|---------------|----------------|------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | 引用数据库 |
| `DASHSCOPE_API_KEY` | `你的 API Key` | AI 服务密钥 |

**操作步骤**：
1. 点击 "New Variable"
2. 输入 Variable Name 和 Value
3. 点击 "Add"
4. 所有变量添加完成后，点击 "Deploy"

---

### 步骤 3: 配置 Docker 镜像

访问：
```
https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/settings
```

**配置 Docker 镜像**：
1. 向下滚动到 **"Deploy"** 部分
2. 找到 **"Docker Image"** 或 **"Connect Image"**
3. 点击后选择 **"Use existing image"**
4. 选择 **global-insight** 服务的镜像
5. 点击 "Save"

---

### 步骤 4: 配置 Start Command

在同一页面的 **"Deploy"** 部分：

1. 找到 **"Start Command"** 输入框
2. 输入：
   ```
   python backend/cron_tasks.py fetch-market
   ```
3. 点击 "Save"

---

### 步骤 5: 配置 Cron Schedule

在同一页面的 **"Cron Schedule"** 部分：

1. 找到 **"Cron Schedule"** 区域
2. 点击 **"Add Schedule"** 或 **"Edit"**
3. 选择 **"Custom"**
4. 输入 Cron 表达式：
   ```
   0 * * * *
   ```
5. 点击 "Save"
6. 点击 **"Deploy"** 应用所有更改

---

### 步骤 6: 验证配置

#### 6.1 检查服务状态

访问：
```
https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9
```

**确认**：
- [ ] 服务状态显示 "Online"
- [ ] 没有错误提示

#### 6.2 检查 Cron Runs

访问：
```
https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/schedule
```

**确认**：
- [ ] 有执行记录
- [ ] 执行状态是 "Success"（绿色）
- [ ] 查看日志确认没有错误

#### 6.3 验证数据更新

等待 5-10 分钟后，访问：
```bash
curl https://global-insight-production.up.railway.app/api/v1/health
```

**预期结果**：
```json
{
  "status": "healthy",
  "database": "connected",
  "data_fresh": true,
  "market_count": 34015  // 数字应该增加
}
```

---

## 🔍 故障排查

### 问题 1: Cron 不执行

**检查清单**：
1. [ ] Cron Schedule 是否已设置？（不是 "No schedule"）
2. [ ] Start Command 是否正确？
3. [ ] Docker 镜像是否已连接？
4. [ ] 环境变量是否已配置？

**解决方法**：
- 重新检查 Settings 页面的配置
- 查看 Deployments 日志

---

### 问题 2: Cron 执行失败

**查看错误日志**：
1. 访问 Cron Runs 页面
2. 点击失败的执行记录
3. 查看 "Logs" 标签页

**常见错误**：

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `DATABASE_URL not set` | 环境变量未配置 | 重新配置 DATABASE_URL |
| `DASHSCOPE_API_KEY invalid` | API Key 无效 | 检查 API Key 是否正确 |
| `ModuleNotFoundError` | 依赖缺失 | 检查 requirements.txt |
| `Connection refused` | 数据库连接失败 | 检查 DATABASE_URL 格式 |

---

### 问题 3: 数据不更新

**检查步骤**：
1. [ ] Cron 执行是否成功？
2. [ ] 日志中是否有错误？
3. [ ] 数据库连接是否正常？
4. [ ] API 调用是否成功？

**调试方法**：
```bash
# 检查当前数据
curl https://global-insight-production.up.railway.app/api/v1/market?limit=3

# 检查健康状态
curl https://global-insight-production.up.railway.app/api/v1/health
```

---

## 📝 其他 Cron 服务配置

创建其他 3 个 Cron 服务，重复上述步骤：

### fetch-news

| 配置项 | 值 |
|--------|-----|
| 服务名称 | fetch-news |
| Schedule | `0 6,18 * * *` |
| Start Command | `python backend/cron_tasks.py fetch-news` |
| DATABASE_URL | `${{Postgres.DATABASE_URL}}` |
| DASHSCOPE_API_KEY | (同上) |

### generate-insights

| 配置项 | 值 |
|--------|-----|
| 服务名称 | generate-insights |
| Schedule | `0 7 * * *` |
| Start Command | `python backend/cron_tasks.py generate-insights` |
| DATABASE_URL | `${{Postgres.DATABASE_URL}}` |
| DASHSCOPE_API_KEY | (同上) |

### build-graph

| 配置项 | 值 |
|--------|-----|
| 服务名称 | build-graph |
| Schedule | `30 7,19 * * *` |
| Start Command | `python backend/cron_tasks.py build-graph` |
| DATABASE_URL | `${{Postgres.DATABASE_URL}}` |
| DASHSCOPE_API_KEY | (同上) |

---

## 🎯 Cron Schedule 参考

```
* * * * *
│ │ │ │ │
│ │ │ │ └─────────── 星期 (0-6, 0=周日)
│ │ │ └───────────── 月份 (1-12)
│ │ └─────────────── 日期 (1-31)
│ └───────────────── 小时 (0-23)
└─────────────────── 分钟 (0-59)
```

### 常用表达式

| Schedule | 含义 | 示例用途 |
|----------|------|----------|
| `0 * * * *` | 每小时 0 分 | 市场数据抓取 |
| `0 6,18 * * *` | 每天 6:00 和 18:00 | 新闻抓取 |
| `0 7 * * *` | 每天 7:00 | AI 洞察生成 |
| `30 7,19 * * *` | 每天 7:30 和 19:30 | 知识图谱构建 |
| `*/15 * * * *` | 每 15 分钟 | 高频监控 |
| `0 0 * * *` | 每天 0:00 | 每日备份 |

---

## ✅ 配置检查清单

### efficient-creativity (Cron 1)
- [ ] 服务已创建
- [ ] Docker 镜像已连接（使用 global-insight 的镜像）
- [ ] Start Command: `python backend/cron_tasks.py fetch-market`
- [ ] Cron Schedule: `0 * * * *`
- [ ] DATABASE_URL: `${{Postgres.DATABASE_URL}}`
- [ ] DASHSCOPE_API_KEY: 已设置
- [ ] 部署完成
- [ ] Cron Runs 有成功执行记录
- [ ] 数据已更新

### fetch-news (Cron 2)
- [ ] 服务已创建
- [ ] Start Command: `python backend/cron_tasks.py fetch-news`
- [ ] Cron Schedule: `0 6,18 * * *`
- [ ] 环境变量已配置
- [ ] 部署完成

### generate-insights (Cron 3)
- [ ] 服务已创建
- [ ] Start Command: `python backend/cron_tasks.py generate-insights`
- [ ] Cron Schedule: `0 7 * * *`
- [ ] 环境变量已配置
- [ ] 部署完成

### build-graph (Cron 4)
- [ ] 服务已创建
- [ ] Start Command: `python backend/cron_tasks.py build-graph`
- [ ] Cron Schedule: `30 7,19 * * *`
- [ ] 环境变量已配置
- [ ] 部署完成

---

## 🔗 快速链接

| 服务 | Settings | Variables | Schedule |
|------|----------|-----------|----------|
| efficient-creativity | [访问](https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/settings) | [访问](https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/variables) | [访问](https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/schedule) |
| global-insight | [访问](https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/fee2b7f1-a3e5-4383-a7d2-c633fd4c83e9) |
| Postgres | [访问](https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/34a09351-2a96-43d0-a9ec-330e2f9051be) |

---

**配置完成后，等待 5-10 分钟检查数据是否更新！** 🚀
