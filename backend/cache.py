#!/usr/bin/env python3
"""
Redis 缓存模块
- 缓存热点数据
- 提升 API 响应速度
- 自动过期管理
"""
import json
import redis
from datetime import timedelta
from typing import Any, Optional

# Redis 配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
DEFAULT_EXPIRE = 300  # 5 分钟

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5
        )
        self.prefix = 'finance:'
    
    def _key(self, key: str) -> str:
        """生成带前缀的键"""
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            data = self.redis.get(self._key(key))
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"❌ 缓存读取失败：{e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = DEFAULT_EXPIRE):
        """设置缓存"""
        try:
            self.redis.setex(
                self._key(key),
                timedelta(seconds=expire),
                json.dumps(value, ensure_ascii=False)
            )
        except Exception as e:
            print(f"❌ 缓存写入失败：{e}")
    
    def delete(self, key: str):
        """删除缓存"""
        try:
            self.redis.delete(self._key(key))
        except Exception as e:
            print(f"❌ 缓存删除失败：{e}")
    
    def clear_pattern(self, pattern: str):
        """批量删除匹配模式的缓存"""
        try:
            keys = self.redis.keys(self._key(pattern))
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            print(f"❌ 批量删除失败：{e}")
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        try:
            info = self.redis.info('stats')
            db_size = self.redis.dbsize()
            return {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'total_keys': db_size,
                'hit_rate': self._calc_hit_rate(info)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calc_hit_rate(self, info: dict) -> float:
        """计算命中率"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        if total == 0:
            return 0.0
        return round(hits / total * 100, 2)

# 全局缓存实例
cache = CacheManager()

# 缓存装饰器
def cached(key_prefix: str, expire: int = DEFAULT_EXPIRE):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # 生成缓存键
                cache_key = f"{key_prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
                
                # 尝试从缓存获取
                result = cache.get(cache_key)
                if result is not None:
                    return result
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 写入缓存
                if result is not None:
                    cache.set(cache_key, result, expire)
                
                return result
            except Exception as e:
                # 缓存失败时直接调用函数
                print(f"⚠️ 缓存异常：{e}")
                return func(*args, **kwargs)
        return wrapper
    return decorator

# 测试
if __name__ == '__main__':
    print("🧪 测试 Redis 缓存...")
    
    # 测试连接
    try:
        cache.redis.ping()
        print("✅ Redis 连接成功")
    except Exception as e:
        print(f"❌ Redis 连接失败：{e}")
        exit(1)
    
    # 测试读写
    cache.set('test', {'hello': 'world'}, 60)
    result = cache.get('test')
    print(f"✅ 缓存测试：{result}")
    
    # 测试统计
    stats = cache.get_stats()
    print(f"📊 缓存统计：{stats}")
    
    # 清理测试
    cache.delete('test')
    print("✅ 测试完成")
