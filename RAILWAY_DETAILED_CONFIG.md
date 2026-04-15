# Railway Cron 详细配置指南

**更新时间**: 2026-04-14 14:41  
**项目**: zestful-education  
**环境**: production

---

## 📋 项目架构

```
Project: zestful-education
├── global-insight (主后端服务)
│   ├── URL: https://global-insight-production.up.railway.app
│   ├── Docker: ✅ 已配置
│   └── Command: uvicorn api:app --host 0.0.0.0 --port $PORT
│
├── Postgres (数据库)
│   ├── DATABASE_URL: ✅ 已生成
│   └── 自动提供环境变量
│
└── efficient-creativity (Cron 服务 - 新建)
    ├── Docker: ⚠️ 需要配置
    ├── Command: ⚠️ 需要配置
    └── Variables: ⚠️ 需要配置
```

---

## 🔧 配置步骤

### 步骤 1: 配置 Cron 服务的 Docker 镜像

1. **访问 Cron 服务的 Settings 页面**
   ```
   https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/settings
   ```

2. **找到 "Deploy" 部分**
   - 向下滚动到 "Deploy" 区域
   - 找到 "Docker Image" 或 "Connect Image" 选项

3. **连接 Docker 镜像**
   - 点击 "Connect Image" 或 "Docker Image"
   - 选择 "Use existing image" 或类似选项
   - 选择 **global-insight** 服务的镜像
   - 或者手动输入镜像名称（如果有）

4. **配置 Start Command**
   - 找到 "Start Command" 输入框
   - 输入：
     ```
     python backend/cron_tasks.py fetch-market
     ```
   - 点击 "Save" 或 "Apply"

---

### 步骤 2: 配置环境变量

1. **访问 Variables 页面**
   ```
   https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/variables
   ```

2. **添加 DATABASE_URL**
   - 点击 "New Variable"
   - Variable Name: `DATABASE_URL`
   - Variable Value: `${{Postgres.DATABASE_URL}}`
   - 点击 "Add"

3. **添加 DASHSCOPE_API_KEY**（如果还没有）
   - 点击 "New Variable"
   - Variable Name: `DASHSCOPE_API_KEY`
   - Variable Value: `你的 DashScope API Key`
   - 点击 "Add"

4. **部署更改**
   - 点击页面底部的 "Deploy" 按钮
   - 等待部署完成

---

### 步骤 3: 验证 Cron Schedule

1. **访问 Settings 页面**
   ```
   https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/settings
   ```

2. **找到 "Cron Schedule" 部分**
   - 确认 Schedule 是：`0 * * * *`（每小时执行）
   - 如果不是，点击 "Edit" 并修改

3. **验证配置**
   - 应该显示：`Every hour (UTC)`

---

### 步骤 4: 查看 Cron 运行日志

1. **访问 Cron Runs 页面**
   ```
   https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9/schedule
   ```

2. **查看运行记录**
   - 查看 "Recent Runs" 或 "Execution History"
   - 确认任务是否成功执行
   - 查看日志了解错误信息

---

## 📝 创建其他 Cron 服务

重复以上步骤，创建以下 3 个额外的 Cron 服务：

### Cron 服务 2: fetch-news

| 配置项 | 值 |
|--------|-----|
| 服务名称 | fetch-news（或类似名称） |
| Schedule | `0 6,18 * * *` |
| Start Command | `python backend/cron_tasks.py fetch-news` |
| DATABASE_URL | `${{Postgres.DATABASE_URL}}` |
| DASHSCOPE_API_KEY | (同上) |

### Cron 服务 3: generate-insights

| 配置项 | 值 |
|--------|-----|
| 服务名称 | generate-insights |
| Schedule | `0 7 * * *` |
| Start Command | `python backend/cron_tasks.py generate-insights` |
| DATABASE_URL | `${{Postgres.DATABASE_URL}}` |
| DASHSCOPE_API_KEY | (同上) |

### Cron 服务 4: build-graph

| 配置项 | 值 |
|--------|-----|
| 服务名称 | build-graph |
| Schedule | `30 7,19 * * *` |
| Start Command | `python backend/cron_tasks.py build-graph` |
| DATABASE_URL | `${{Postgres.DATABASE_URL}}` |
| DASHSCOPE_API_KEY | (同上) |

---

## 🔍 故障排查

### Cron 不执行？

1. **检查环境变量**
   ```
   Variables 页面确认：
   - DATABASE_URL 已设置
   - DASHSCOPE_API_KEY 已设置
   ```

2. **检查 Docker 镜像**
   ```
   Settings 页面确认：
   - Docker Image 已连接
   - Start Command 正确
   ```

3. **检查 Cron Schedule**
   ```
   Settings 页面确认：
   - Schedule 已设置
   - 不是 "No schedule"
   ```

4. **查看日志**
   ```
   Cron Runs 页面：
   - 查看最近执行记录
   - 点击执行记录查看详细日志
   ```

### Cron 执行失败？

1. **查看错误日志**
   - 在 Cron Runs 页面点击失败的执行记录
   - 查看 "Logs" 标签页

2. **常见问题**
   - 数据库连接失败 → 检查 DATABASE_URL
   - API Key 无效 → 检查 DASHSCOPE_API_KEY
   - 代码错误 → 查看日志中的 Python 错误信息

---

## 📊 Cron Schedule 参考

```
* * * * *
│ │ │ │ │
│ │ │ │ └─────────── 星期 (0-6, 0=周日)
│ │ │ └───────────── 月份 (1-12)
│ │ └─────────────── 日期 (1-31)
│ └───────────────── 小时 (0-23)
└─────────────────── 分钟 (0-59)
```

### 示例

| Schedule | 含义 |
|----------|------|
| `0 * * * *` | 每小时 0 分 |
| `0 6,18 * * *` | 每天 6:00 和 18:00 |
| `0 7 * * *` | 每天 7:00 |
| `30 7,19 * * *` | 每天 7:30 和 19:30 |
| `*/15 * * * *` | 每 15 分钟 |
| `0 0 * * *` | 每天 0:00（午夜） |

---

## ✅ 配置检查清单

### efficient-creativity (Cron 1)
- [ ] Docker 镜像已连接
- [ ] Start Command: `python backend/cron_tasks.py fetch-market`
- [ ] DATABASE_URL: `${{Postgres.DATABASE_URL}}`
- [ ] DASHSCOPE_API_KEY: 已设置
- [ ] Cron Schedule: `0 * * * *`
- [ ] 部署完成

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

| 服务 | 链接 |
|------|------|
| efficient-creativity (Cron 1) | [访问服务](https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/8a4bf064-947e-4d01-aa80-6ae20b7166e9) |
| global-insight (主服务) | [访问服务](https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/fee2b7f1-a3e5-4383-a7d2-c633fd4c83e9) |
| Postgres (数据库) | [访问服务](https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f/service/34a09351-2a96-43d0-a9ec-330e2f9051be) |
| 项目总览 | [访问项目](https://railway.com/project/5e1c61e5-8994-465c-ae6a-7ad52501206f) |

---

**配置完成！** 🎉
