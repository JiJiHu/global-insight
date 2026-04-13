#!/usr/bin/env python3
"""
缓存统计 API
"""
from cache import cache

if __name__ == '__main__':
    print("📊 缓存统计:")
    stats = cache.get_stats()
    
    print(f"  命中数：{stats.get('hits', 0)}")
    print(f"  未命中：{stats.get('misses', 0)}")
    print(f"  命中率：{stats.get('hit_rate', 0)}%")
    print(f"  总键数：{stats.get('total_keys', 0)}")
