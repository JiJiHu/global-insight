# Global Insight AI 洞察配置指南

**更新时间**: 2026-03-13  
**AI 模型**: dashscope-cp/qwen3.5-plus

---

## 🎯 功能说明

AI 洞察生成器 v3 使用真正的 AI 模型（Qwen3.5-Plus）分析市场数据和新闻，生成深度投资洞察。

### 主要功能

1. **AI 市场深度分析**
   - 分析 20 只股票的最新行情
   - 识别市场趋势和风险点
   - 提供具体投资建议

2. **AI 新闻摘要**
   - 总结 24 小时内的重要新闻
   - 提炼市场影响和明日展望
   - 突出关键信息

---

## 🔑 配置步骤

### 步骤 1：获取 API Key

访问阿里云 DashScope 控制台：
```
https://dashscope.console.aliyun.com/
```

1. 登录阿里云账号
2. 进入 DashScope 控制台
3. 创建或查看 API Key

### 步骤 2：配置 API Key

**方法 A：使用配置脚本（推荐）**
```bash
bash /root/global-insight/config-dashscope.sh
```

按提示输入 API Key，脚本会自动：
- ✅ 设置环境变量
- ✅ 更新 ~/.bashrc
- ✅ 重启 Docker 服务
- ✅ 验证配置

**方法 B：手动配置**
```bash
# 1. 设置环境变量
export DASHSCOPE_API_KEY="sk-your-api-key"

# 2. 添加到 ~/.bashrc (永久生效)
echo "export DASHSCOPE_API_KEY=\"sk-your-api-key\"" >> ~/.bashrc
source ~/.bashrc

# 3. 重启服务
cd /root/global-insight
docker-compose up -d --force-recreate backend
```

### 步骤 3：验证配置

```bash
# 运行测试脚本
bash /root/global-insight/test-ai-insights.sh
```

**预期输出**:
```
✅ API Key 已配置
🚀 运行 AI 洞察生成...
🧠 正在调用 Qwen3.5-Plus 生成分析...
✅ AI 分析生成成功
💾 保存洞察到数据库...
✅ 完成！共生成了 2 条 AI 洞察
```

---

## ⚙️ 定时任务配置

### 添加 AI 洞察定时任务

```bash
# 每小时生成一次 AI 洞察
(crontab -l 2>/dev/null | grep -v "generate_ai_insights_v3" || true; \
echo "0 * * * * docker exec global-insight-backend python3 /app/generate_ai_insights_v3.py >> /var/log/global-insight/ai-insights.log 2>&1") | crontab -
```

### 查看定时任务

```bash
crontab -l | grep insight
```

**预期输出**:
```bash
0 * * * * docker exec global-insight-backend python3 /app/generate_insights_v2.py >> /var/log/global-insight/insights.log 2>&1
0 * * * * docker exec global-insight-backend python3 /app/generate_ai_insights_v3.py >> /var/log/global-insight/ai-insights.log 2>&1
```

---

## 📊 查看 AI 洞察

### 方法 1：访问前端页面

打开浏览器访问：
```
http://150.40.177.181:11279
```

在"AI 洞察"卡片中查看最新的 AI 分析。

### 方法 2：API 查询

```bash
curl http://localhost:11279/api/v1/insights?limit=10 | python3 -m json.tool
```

### 方法 3：查看日志

```bash
tail -f /var/log/global-insight/ai-insights.log
```

---

## 🔍 故障排查

### 问题 1：API Key 未配置

**错误信息**:
```
❌ 未配置 DASHSCOPE_API_KEY 环境变量
```

**解决方案**:
```bash
bash /root/global-insight/config-dashscope.sh
```

### 问题 2：API 调用失败

**可能原因**:
- API Key 无效
- 网络问题
- 额度不足

**检查步骤**:
```bash
# 1. 验证 API Key 格式
echo $DASHSCOPE_API_KEY

# 2. 测试 API 连接
curl -X POST "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.5-plus","messages":[{"role":"user","content":"你好"}]}'

# 3. 检查 DashScope 控制台额度
```

### 问题 3：洞察未生成

**检查日志**:
```bash
docker logs global-insight-backend 2>&1 | tail -50
```

**手动运行测试**:
```bash
docker exec global-insight-backend python3 generate_ai_insights_v3.py
```

---

## 💰 费用说明

### Qwen3.5-Plus 定价

- **输入**: ¥0.002 / 1K tokens
- **输出**: ¥0.006 / 1K tokens

### 预估成本

每次生成约消耗：
- 输入：~500 tokens（市场数据 + 新闻）
- 输出：~800 tokens（分析内容）

**单次成本**: 约 ¥0.006
**每小时一次**: 约 ¥0.14/天
**每月成本**: 约 ¥4.32

---

## 📈 优化建议

### 1. 调整生成频率

根据需求调整定时任务频率：

```bash
# 每 4 小时一次（降低成本）
0 */4 * * * docker exec global-insight-backend python3 /app/generate_ai_insights_v3.py

# 每天上午 9 点一次（仅工作日）
0 9 * * 1-5 docker exec global-insight-backend python3 /app/generate_ai_insights_v3.py
```

### 2. 控制输出长度

修改 `generate_ai_insights_v3.py` 中的 `max_tokens` 参数：

```python
payload = {
    'model': MODEL,
    'messages': [...],
    'temperature': 0.7,
    'max_tokens': 500  # 减少输出长度，降低成本
}
```

### 3. 混合模式

- **基础洞察**: 基于规则（免费，每小时）
- **深度分析**: AI 生成（付费，每天 1-2 次）

---

## 🎯 最佳实践

### 1. 监控使用情况

定期检查 DashScope 控制台：
- API 调用次数
- Token 消耗量
- 剩余额度

### 2. 设置预算告警

在 DashScope 控制台设置：
- 每日预算上限
- 用量告警通知

### 3. 备份配置

```bash
# 备份 API Key
echo $DASHSCOPE_API_KEY > /root/.dashscope_api_key.backup
chmod 600 /root/.dashscope_api_key.backup
```

---

## 📝 相关文件

| 文件 | 说明 |
|------|------|
| `generate_ai_insights_v3.py` | AI 洞察生成脚本 |
| `config-dashscope.sh` | API Key 配置脚本 |
| `test-ai-insights.sh` | 测试脚本 |
| `docker-compose.yml` | Docker 配置（已添加 API Key 环境变量） |

---

## 🆘 获取帮助

### 查看文档

```bash
cat /root/global-insight/AI_INSIGHTS_GUIDE.md
```

### 测试 API

```bash
bash /root/global-insight/test-ai-insights.sh
```

### 重新配置

```bash
bash /root/global-insight/config-dashscope.sh
```

---

**配置完成时间**: 2026-03-13  
**AI 模型**: Qwen3.5-Plus (dashscope-cp)  
**状态**: 🎉 准备就绪
