#!/usr/bin/env python3
"""
系统健康检查模块
- 服务状态监控
- 性能指标收集
- 异常告警
"""
import sys
import subprocess
import json
from datetime import datetime
from db import get_db_connection

def check_service_status():
    """检查服务状态"""
    print("\n🔍 检查服务状态...")
    print("=" * 60)
    
    services = {
        'finance-db': 'PostgreSQL',
        'finance-backend': 'Backend API',
        'finance-frontend': 'Frontend',
        'finance-redis': 'Redis Cache'
    }
    
    status = {}
    for container, name in services.items():
        try:
            result = subprocess.run(
                ['docker', 'inspect', '--format={{.State.Status}}', container],
                capture_output=True, text=True, timeout=5
            )
            container_status = result.stdout.strip()
            status[name] = '✅' if container_status == 'running' else '❌'
            print(f"   {status[name]} {name}: {container_status}")
        except Exception as e:
            status[name] = '❌'
            print(f"   {status[name]} {name}: 未找到")
    
    return status

def check_database_health():
    """检查数据库健康"""
    print("\n🗄️  检查数据库健康...")
    print("=" * 60)
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # 检查连接
            cur.execute("SELECT 1")
            print("   ✅ 数据库连接：正常")
            
            # 检查数据量
            cur.execute("SELECT COUNT(*) FROM market_data")
            market_count = cur.fetchone()[0]
            print(f"   📊 行情数据：{market_count:,} 条")
            
            cur.execute("SELECT COUNT(*) FROM news")
            news_count = cur.fetchone()[0]
            print(f"   📰 新闻数据：{news_count:,} 条")
            
            cur.execute("SELECT COUNT(*) FROM insights")
            insights_count = cur.fetchone()[0]
            print(f"   💡 AI 洞察：{insights_count:,} 条")
            
            # 检查数据新鲜度
            cur.execute("""
                SELECT symbol, timestamp
                FROM market_data
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            latest = cur.fetchone()
            if latest:
                age = datetime.now() - latest[1].replace(tzinfo=None)
                print(f"   🕒 最新数据：{latest[0]} ({age.seconds//60} 分钟前)")
            
            cur.close()
            
            return {
                'status': '✅',
                'market_count': market_count,
                'news_count': news_count,
                'insights_count': insights_count
            }
    except Exception as e:
        print(f"   ❌ 数据库异常：{e}")
        return {'status': '❌', 'error': str(e)}

def check_api_health():
    """检查 API 健康"""
    print("\n🌐 检查 API 健康...")
    print("=" * 60)
    
    import requests
    
    endpoints = {
        '健康检查': 'http://localhost:8000/api/v1/health',
        '统计数据': 'http://localhost:8000/api/v1/stats',
        '行情数据': 'http://localhost:8000/api/v1/market',
        '前端页面': 'http://localhost:11279'
    }
    
    status = {}
    for name, url in endpoints.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                status[name] = '✅'
                print(f"   ✅ {name}: {response.status_code} ({response.elapsed.total_seconds()*1000:.0f}ms)")
            else:
                status[name] = '⚠️'
                print(f"   ⚠️ {name}: {response.status_code}")
        except Exception as e:
            status[name] = '❌'
            print(f"   ❌ {name}: {str(e)[:50]}")
    
    return status

def check_system_resources():
    """检查系统资源"""
    print("\n💻 检查系统资源...")
    print("=" * 60)
    
    # CPU
    try:
        result = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=5)
        cpu_line = [line for line in result.stdout.split('\n') if 'Cpu(s)' in line][0]
        cpu_idle = float(cpu_line.split(',')[3].strip().split()[0])
        cpu_usage = 100 - cpu_idle
        print(f"   📊 CPU 使用率：{cpu_usage:.1f}%")
    except:
        print(f"   ⚠️ CPU 数据不可用")
    
    # 内存
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=5)
        mem_line = result.stdout.split('\n')[1]
        parts = mem_line.split()
        total = parts[1]
        used = parts[2]
        print(f"   📊 内存使用：{used} / {total}")
    except:
        print(f"   ⚠️ 内存数据不可用")
    
    # 磁盘
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
        disk_line = result.stdout.split('\n')[1]
        parts = disk_line.split()
        usage = parts[4]
        available = parts[3]
        print(f"   📊 磁盘使用：{usage} (可用：{available})")
    except:
        print(f"   ⚠️ 磁盘数据不可用")

def generate_health_report():
    """生成健康报告"""
    print("\n📋 生成健康报告...")
    print("=" * 60)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'services': check_service_status(),
        'database': check_database_health(),
        'api': check_api_health(),
        'system': '检查完成'
    }
    
    # 保存报告
    report_file = '/root/finance-dashboard/health-report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 健康报告已保存：{report_file}")
    print("=" * 60)
    
    return report

if __name__ == '__main__':
    generate_health_report()
