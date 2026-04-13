#!/usr/bin/env python3
"""
简单的内存缓存模块
用于缓存 API 响应，减少数据库查询
"""
import time
from functools import wraps
from typing import Any, Dict, Optional
import hashlib
import json

class SimpleCache:
    """简单的内存缓存"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl  # 默认 5 分钟
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        if time.time() > item['expires']:
            # 过期删除
            del self.cache[key]
            return None
        
        return item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        # 如果缓存已满，删除最旧的
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['expires'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'expires': time.time() + (ttl or self.default_ttl)
        }
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
    
    def cleanup(self) -> int:
        """清理过期缓存，返回清理数量"""
        expired_keys = [
            k for k, v in self.cache.items()
            if time.time() > v['expires']
        ]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)

# 全局缓存实例
api_cache = SimpleCache(max_size=100, default_ttl=300)  # 5 分钟 TTL

def cached(ttl: Optional[int] = None):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{api_cache._generate_key(*args, **kwargs)}"
            
            # 尝试获取缓存
            cached_result = api_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            api_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# 定期清理任务
def cleanup_cache():
    """清理过期缓存"""
    cleaned = api_cache.cleanup()
    if cleaned > 0:
        print(f"🧹 清理了 {cleaned} 个过期缓存项")

if __name__ == "__main__":
    # 测试
    @cached(ttl=10)
    def expensive_query(limit: int):
        print(f"执行查询... limit={limit}")
        return list(range(limit))
    
    print("第一次调用:")
    result1 = expensive_query(10)
    
    print("\n第二次调用（应该命中缓存）:")
    result2 = expensive_query(10)
    
    print("\n10 秒后调用（缓存过期）:")
    import time
    time.sleep(11)
    result3 = expensive_query(10)
