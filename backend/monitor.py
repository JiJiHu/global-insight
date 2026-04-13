#!/usr/bin/env python3
"""
监控告警脚本
- 检查数据新鲜度
- 检查 API 健康
- 发送告警通知
"""
import sys
sys.path.insert(0, '/app')

from datetime import datetime, timedelta, timezone
from db import get_db_connection
import requests
import os

# 配置
ALERT_THRESHOLD_HOURS = 24  # 数据超过 24 小时未更新告警
HEALTH_CHECK_URL = "http://localhost:8000/api/v1/health"

def check_data_freshness():
    """检查数据新鲜度"""
    print("📊 检查数据新鲜度...")
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 检查最新新闻时间
        cur.execute("SELECT MAX(created_at), source FROM news GROUP BY source ORDER BY MAX(created_at) DESC LIMIT 5")
        results = cur.fetchall()
        
        alerts = []
        now = datetime.now(timezone.utc)
        
        for latest_time, source in results:
            if latest_time.tzinfo is None:
                latest_time = latest_time.replace(tzinfo=timezone.utc)
            
            age_hours = (now - latest_time).total_seconds() / 3600
            
            status = "✅" if age_hours < ALERT_THRESHOLD_HOURS else "⚠️"
            print(f"  {status} {source:25} {age_hours:.1f}小时前")
            
            if age_hours >= ALERT_THRESHOLD_HOURS:
                alerts.append(f"⚠️ {source} 数据已过时 {age_hours:.1f} 小时")
        
        cur.close()
        return alerts

def check_api_health():
    """检查 API 健康状态"""
    print("\n🏥 检查 API 健康...")
    
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=10)
        health = response.json()
        
        if health.get('status') == 'healthy':
            print(f"  ✅ API 健康")
            stats = health.get('stats', {})
            print(f"     新闻：{stats.get('news_count', 0)} 条")
            print(f"     市场：{stats.get('market_count', 0)} 条")
            print(f"     数据新鲜：{'✅' if stats.get('data_fresh') else '⚠️'}")
            return []
        else:
            return ["⚠️ API 状态异常"]
    
    except Exception as e:
        print(f"  ❌ API 检查失败：{e}")
        return [f"❌ API 健康检查失败：{e}"]

def check_disk_usage():
    """检查磁盘使用率"""
    print("\n💾 检查磁盘使用...")
    
    import shutil
    
    # 检查项目目录
    total, used, free = shutil.disk_usage('/')
    usage_percent = (used / total) * 100
    
    status = "✅" if usage_percent < 80 else "⚠️"
    print(f"  {status} 使用率：{usage_percent:.1f}% ({used//1e9}GB / {total//1e9}GB)")
    
    if usage_percent >= 80:
        return [f"⚠️ 磁盘使用率超过 80%: {usage_percent:.1f}%"]
    return []

def send_alert(message: str):
    """发送告警（可扩展为邮件、钉钉等）"""
    print(f"\n🚨 告警：{message}")
    # TODO: 集成钉钉/邮件告警

def run_monitor():
    """运行监控检查"""
    print("=" * 60)
    print(f"🔍 Global Insight 监控检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_alerts = []
    
    # 执行检查
    all_alerts.extend(check_data_freshness())
    all_alerts.extend(check_api_health())
    all_alerts.extend(check_disk_usage())
    
    # 汇总
    print("\n" + "=" * 60)
    if all_alerts:
        print(f"🚨 发现 {len(all_alerts)} 个告警:")
        for alert in all_alerts:
            print(f"  - {alert}")
            send_alert(alert)
    else:
        print("✅ 所有检查通过，系统运行正常")
    print("=" * 60)
    
    return len(all_alerts)

if __name__ == "__main__":
    alert_count = run_monitor()
    sys.exit(0 if alert_count == 0 else 1)
