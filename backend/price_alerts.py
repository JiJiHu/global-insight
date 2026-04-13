#!/usr/bin/env python3
"""
价格波动告警脚本
- 监控价格大幅波动（>5%）
- 发送告警通知到 WhatsApp
- 每个股票每天只告警一次
"""
import sys
import subprocess
from datetime import datetime, timedelta
sys.path.insert(0, '/root/finance-dashboard/backend')

from db import get_db_connection

# 告警阈值
PRICE_CHANGE_THRESHOLD = 5.0  # 涨跌幅超过 5% 告警
WHATSAPP_TARGET = "+5511996909894"

def get_today_alerted_symbols():
    """获取今天已经告警过的股票列表"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT symbol 
            FROM price_alerts 
            WHERE alert_time::date = CURRENT_DATE
        """)
        symbols = {row[0] for row in cur.fetchall()}
        cur.close()
    return symbols

def send_alert_notification(alerts):
    """通过 OpenClaw 发送告警到 WhatsApp"""
    if not alerts:
        return
    
    print("\n📱 发送告警通知...")
    
    # 构建告警消息
    message = "🚨 **价格波动告警**\n\n"
    
    for alert in alerts[:5]:  # 最多发送 5 个
        direction = alert['direction']
        symbol = alert['symbol']
        sentiment = alert['sentiment']
        change = abs(alert['change_percent'])
        price = alert['current_price']
        
        message += f"{direction} **{symbol}** {sentiment} {change:.2f}%\n"
        message += f"   当前价格：${price:.2f}\n\n"
    
    if len(alerts) > 5:
        message += f"\n... 还有 {len(alerts) - 5} 个告警，请查看仪表盘\n"
    
    message += f"\n⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    message += f"\n🌐 查看：http://localhost:3000"
    
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
            print(f"✅ 告警通知已发送")
        else:
            print(f"⚠️ 发送失败：{result.stderr}")
    except Exception as e:
        print(f"⚠️ 发送异常：{e}")

def check_price_alerts():
    """检查价格波动告警（每个股票每天只告警一次）"""
    print(f"\n🔔 检查价格告警 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取今天已告警的股票
    today_alerted = get_today_alerted_symbols()
    if today_alerted:
        print(f"📋 今天已告警股票: {', '.join(today_alerted)}")
    
    alerts = []
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取最新价格数据
        cur.execute("""
            WITH latest_data AS (
                SELECT DISTINCT ON (symbol)
                    symbol, type, price, change_percent, timestamp
                FROM market_data
                ORDER BY symbol, timestamp DESC
            )
            SELECT 
                symbol, type, price as current_price, change_percent, timestamp
            FROM latest_data
            WHERE ABS(change_percent) > %s
            ORDER BY ABS(change_percent) DESC
        """, (PRICE_CHANGE_THRESHOLD,))
        
        results = cur.fetchall()
        cur.close()
        
        for row in results:
            symbol, type_, current_price, change_percent, timestamp = row
            
            # 跳过今天已告警的股票
            if symbol in today_alerted:
                print(f"⏭️ {symbol} 今天已告警，跳过")
                continue
            
            # 判断涨跌
            direction = "📈" if change_percent > 0 else "📉"
            sentiment = "大涨" if change_percent > 0 else "大跌"
            
            alert = {
                'symbol': symbol,
                'type': type_,
                'current_price': current_price,
                'change_percent': change_percent,
                'timestamp': timestamp,
                'direction': direction,
                'sentiment': sentiment
            }
            alerts.append(alert)
    
    if alerts:
        print(f"\n⚠️ 发现 {len(alerts)} 个新告警！\n")
        for alert in alerts:
            print(f"{alert['direction']} {alert['symbol']} {alert['sentiment']} {abs(alert['change_percent']):.2f}%")
            print(f"   当前价格：${alert['current_price']:.2f}")
            print()
        
        # 发送通知
        send_alert_notification(alerts)
    else:
        print(f"✅ 无新告警（阈值：±{PRICE_CHANGE_THRESHOLD}%）")
    
    print("=" * 60)
    return alerts

def save_alerts_to_db(alerts):
    """保存告警记录到数据库"""
    if not alerts:
        return
    
    print("\n💾 保存告警记录...")
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 创建告警表（如果不存在）
        cur.execute("""
            CREATE TABLE IF NOT EXISTS price_alerts (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                type VARCHAR(20),
                current_price DECIMAL(20, 8),
                change_percent DECIMAL(10, 4),
                previous_price DECIMAL(20, 8),
                alert_time TIMESTAMPTZ DEFAULT NOW(),
                notified BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 插入告警记录
        for alert in alerts:
            cur.execute("""
                INSERT INTO price_alerts 
                (symbol, type, current_price, change_percent)
                VALUES (%s, %s, %s, %s)
            """, (
                alert['symbol'],
                alert['type'],
                alert['current_price'],
                alert['change_percent']
            ))
        
        conn.commit()
        cur.close()
        print(f"✅ 已保存 {len(alerts)} 条告警记录")

if __name__ == "__main__":
    alerts = check_price_alerts()
    save_alerts_to_db(alerts)