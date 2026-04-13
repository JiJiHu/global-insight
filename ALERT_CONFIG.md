# 🚨 价格告警配置说明

**更新时间**: 2026-03-08  
**状态**: ✅ 已启用 WhatsApp 通知

---

## 📋 告警配置

### 告警阈值

| 参数 | 当前值 | 说明 |
|------|--------|------|
| **价格波动** | ±5.0% | 涨跌幅超过此值触发告警 |
| **检查频率** | 每 15 分钟 | cron 任务执行频率 |
| **通知渠道** | WhatsApp | +5511996909894 |
| **最大告警数** | 5 条/次 | 单次最多发送 5 条告警 |

---

## 🔧 修改告警阈值

### 方法 1: 修改配置文件

编辑 `/root/finance-dashboard/backend/price_alerts.py`:

```python
# 第 14 行
PRICE_CHANGE_THRESHOLD = 5.0  # 改为你的阈值，如 3.0 或 7.0
```

### 方法 2: 使用环境变量

```bash
# 在 cron 任务中设置
*/15 * * * * PRICE_CHANGE_THRESHOLD=3.0 /root/finance-dashboard/cron-alerts.sh
```

### 推荐阈值

| 场景 | 推荐阈值 | 说明 |
|------|---------|------|
| **敏感模式** | ±3.0% | 捕捉所有波动，告警频繁 |
| **平衡模式** | ±5.0% | ✅ 当前配置，适中 |
| **保守模式** | ±7.0% | 仅重大波动告警 |
| **极端模式** | ±10.0% | 仅暴跌/暴涨告警 |

---

## 📱 告警消息格式

**示例**:
```
🚨 价格波动告警

📈 AAPL 大涨 6.50%
   当前价格：$275.50

📉 TSLA 大跌 7.20%
   当前价格：$385.00

⏰ 时间：2026-03-08 10:48:24
🌐 查看：http://150.40.177.181:11279
```

---

## 🧪 测试告警

### 手动测试

```bash
# 运行测试脚本
python3 /root/finance-dashboard/test-whatsapp-alert.py
```

### 查看历史告警

```bash
# 查看告警日志
tail -50 /var/log/finance-alerts.log
```

---

## ⏰ 定时任务配置

### 当前配置

```bash
# 查看当前 cron
crontab -l | grep finance

# 输出:
*/15 * * * * /root/finance-dashboard/cron-alerts.sh
```

### 修改频率

```bash
# 编辑 cron
crontab -e

# 每 5 分钟检查（更频繁）
*/5 * * * * /root/finance-dashboard/cron-alerts.sh

# 每 30 分钟检查（较少）
*/30 * * * * /root/finance-dashboard/cron-alerts.sh

# 仅工作时间检查（9:00-18:00）
*/15 9-18 * * * 1-5 /root/finance-dashboard/cron-alerts.sh
```

---

## 📊 告警统计

### 查看告警频率

```bash
# 统计今日告警数
grep "发现.*个价格告警" /var/log/finance-alerts.log | \
  grep $(date +%Y-%m-%d) | wc -l
```

### 查看最常告警的股票

```bash
# 统计告警最多的股票
grep "📈\|📉" /var/log/finance-alerts.log | \
  grep -oE '[A-Z]{4}' | sort | uniq -c | sort -rn | head -10
```

---

## 🔔 免打扰设置

### 设置免打扰时段

编辑 `/root/finance-dashboard/backend/price_alerts.py`:

```python
# 添加免打扰检查
def check_quiet_hours():
    """检查是否在免打扰时段"""
    from datetime import datetime
    now = datetime.now()
    
    # 免打扰：22:00 - 08:00
    if now.hour >= 22 or now.hour <= 8:
        return True
    
    # 周末免打扰（可选）
    # if now.weekday() >= 5:  # 周六=5, 周日=6
    #     return True
    
    return False

# 在 check_price_alerts() 开头添加
if check_quiet_hours():
    print("🌙 免打扰时段，跳过告警")
    return
```

---

## 🎯 最佳实践

### 1. **阈值设置**
- 初期使用 ±5.0%，观察 1 周
- 根据告警频率调整
- 避免过于敏感（告警疲劳）

### 2. **检查频率**
- 默认每 15 分钟（平衡）
- 交易时段可加密到每 5 分钟
- 非交易时段可放宽到每 30 分钟

### 3. **告警优化**
- 设置免打扰时段（22:00-08:00）
- 单次最多 5 条（避免刷屏）
- 优先发送波动最大的

### 4. **日志管理**
```bash
# 每周清理旧日志
0 0 * * 0 find /var/log -name "finance-*.log" -mtime +7 -delete
```

---

## 📱 接收人管理

### 当前接收人

| 号码 | 说明 |
|------|------|
| +5511996909894 | ✅ Jack (主要) |

### 添加多个接收人

编辑 `/root/finance-dashboard/backend/price_alerts.py`:

```python
WHATSAPP_TARGETS = [
    "+5511996909894",  # Jack
    "+8613800138000",  # 接收人 2
    "+1234567890",     # 接收人 3
]

def send_alert_notification(alerts):
    for target in WHATSAPP_TARGETS:
        # 发送消息
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'whatsapp',
            '--target', target,
            '--message', message
        ]
        subprocess.run(cmd)
```

---

## 🚨 故障排查

### 问题 1: 告警未发送

**检查**:
```bash
# 1. 查看日志
tail -50 /var/log/finance-alerts.log

# 2. 检查 cron 状态
systemctl status cron

# 3. 手动运行
/root/finance-dashboard/cron-alerts.sh
```

### 问题 2: WhatsApp 发送失败

**检查**:
```bash
# 1. 测试发送
python3 /root/finance-dashboard/test-whatsapp-alert.py

# 2. 检查 OpenClaw 状态
openclaw status

# 3. 检查 WhatsApp 配置
openclaw channels list
```

### 问题 3: 告警过于频繁

**解决**:
1. 调高阈值（5.0% → 7.0%）
2. 降低检查频率（15 分钟 → 30 分钟）
3. 设置免打扰时段

---

## 📈 告警示例

### 示例 1: 单股票大涨

```
🚨 价格波动告警

📈 **NVDA** 大涨 8.50%
   当前价格：$950.00

⏰ 时间：2026-03-08 14:30:00
🌐 查看：http://150.40.177.181:11279
```

### 示例 2: 多股票波动

```
🚨 价格波动告警

📈 **AAPL** 大涨 6.50%
   当前价格：$275.50

📉 **TSLA** 大跌 7.20%
   当前价格：$385.00

📈 **GOOGL** 大涨 5.80%
   当前价格：$315.00

⏰ 时间：2026-03-08 14:30:00
🌐 查看：http://150.40.177.181:11279
```

---

## ✅ 配置确认

**当前状态**:
- ✅ WhatsApp 告警已启用
- ✅ 测试消息发送成功
- ✅ 定时任务运行正常
- ✅ 阈值：±5.0%
- ✅ 频率：每 15 分钟

**下次检查**: 自动运行，无需手动干预

---

*配置完成时间：2026-03-08*  
*维护者：Jack*
