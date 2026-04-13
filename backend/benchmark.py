#!/usr/bin/env python3
"""
性能基准测试脚本
测试 API 响应时间和数据库查询性能
"""
import sys
import time
import statistics
sys.path.insert(0, '/app')

from db import get_db_connection
import requests

API_BASE = "http://localhost:8000"

def test_db_query():
    """测试数据库查询性能"""
    print("📊 数据库查询性能测试")
    print("=" * 60)
    
    times = []
    
    # 测试 1: 简单查询
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        for i in range(10):
            start = time.time()
            cur.execute("SELECT COUNT(*) FROM news")
            cur.fetchone()
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
        
        cur.close()
    
    print(f"简单查询 (COUNT):")
    print(f"  平均：{statistics.mean(times):.2f}ms")
    print(f"  中位数：{statistics.median(times):.2f}ms")
    print(f"  最小：{min(times):.2f}ms")
    print(f"  最大：{max(times):.2f}ms")
    
    # 测试 2: 带索引查询
    times2 = []
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        for i in range(10):
            start = time.time()
            cur.execute("SELECT id, title FROM news WHERE source = 'Finnhub' ORDER BY created_at DESC LIMIT 100")
            cur.fetchall()
            elapsed = (time.time() - start) * 1000
            times2.append(elapsed)
        
        cur.close()
    
    print(f"\n带索引查询 (source + ORDER BY):")
    print(f"  平均：{statistics.mean(times2):.2f}ms")
    print(f"  中位数：{statistics.median(times2):.2f}ms")
    print(f"  最小：{min(times2):.2f}ms")
    print(f"  最大：{max(times2):.2f}ms")
    
    return times, times2

def test_api_endpoint():
    """测试 API 端点性能"""
    print("\n\n🌐 API 端点性能测试")
    print("=" * 60)
    
    endpoints = [
        ("/api/v1/health", "健康检查"),
        ("/api/v1/news?limit=100", "新闻列表 (100 条)"),
        ("/api/v1/market", "市场数据"),
    ]
    
    for endpoint, name in endpoints:
        times = []
        
        for i in range(5):
            start = time.time()
            response = requests.get(f"{API_BASE}{endpoint}", timeout=30)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            if response.status_code != 200:
                print(f"⚠️ {name} 返回状态码：{response.status_code}")
        
        print(f"\n{name} ({endpoint}):")
        print(f"  平均：{statistics.mean(times):.2f}ms")
        print(f"  中位数：{statistics.median(times):.2f}ms")
        print(f"  最小：{min(times):.2f}ms")
        print(f"  最大：{max(times):.2f}ms")

def test_cache_performance():
    """测试缓存性能"""
    print("\n\n💾 缓存性能测试")
    print("=" * 60)
    
    from utils.cache import api_cache, cached
    
    @cached(ttl=60)
    def cached_query():
        time.sleep(0.1)  # 模拟慢查询
        return "result"
    
    # 第一次调用（未缓存）
    start = time.time()
    cached_query()
    first_call = (time.time() - start) * 1000
    
    # 第二次调用（命中缓存）
    start = time.time()
    cached_query()
    cached_call = (time.time() - start) * 1000
    
    print(f"首次调用（无缓存）: {first_call:.2f}ms")
    print(f"缓存命中：{cached_call:.2f}ms")
    print(f"性能提升：{first_call/cached_call:.1f}x")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Global Insight 性能基准测试")
    print("=" * 60)
    
    test_db_query()
    test_api_endpoint()
    test_cache_performance()
    
    print("\n" + "=" * 60)
    print("✅ 性能测试完成")
    print("=" * 60)
