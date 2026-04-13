#!/usr/bin/env python3
"""
测试 WhatsApp 告警发送
"""
import subprocess
from datetime import datetime

WHATSAPP_TARGET = "+5511996909894"

# 构建测试消息
message = """🚨 **价格波动告警 - 测试**

📈 **AAPL** 大涨 6.50%
   当前价格：$275.50

📉 **TSLA** 大跌 7.20%
   当前价格：$385.00

⏰ 时间：""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
🌐 查看：http://150.40.177.181:11279

---
这是一条测试消息，确认告警系统正常工作。"""

print("📱 发送测试告警到 WhatsApp...")
print(f"目标：{WHATSAPP_TARGET}")
print(f"消息内容:\n{message}\n")

# 使用 OpenClaw CLI 发送
try:
    cmd = [
        'openclaw', 'message', 'send',
        '--channel', 'whatsapp',
        '--target', WHATSAPP_TARGET,
        '--message', message
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("✅ 测试消息发送成功！")
    else:
        print(f"❌ 发送失败：{result.stderr}")
        print(f"stdout: {result.stdout}")
except Exception as e:
    print(f"❌ 发送异常：{e}")
