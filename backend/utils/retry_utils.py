#!/usr/bin/env python3
"""
重试工具模块
为网络请求提供自动重试功能
"""
from functools import wraps
import time
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

# 配置
MAX_RETRIES = 3
BASE_DELAY = 1  # 秒
MAX_DELAY = 10  # 秒

def retry_request(func):
    """
    装饰器：为 HTTP 请求添加重试逻辑
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except (requests.exceptions.Timeout, 
                    requests.exceptions.ConnectionError,
                    requests.exceptions.RequestException) as e:
                last_exception = e
                
                if attempt < MAX_RETRIES - 1:
                    # 指数退避 + 随机抖动
                    delay = min(BASE_DELAY * (2 ** attempt) + random.uniform(0, 1), MAX_DELAY)
                    print(f"⚠️  请求失败，{delay:.1f}秒后重试 ({attempt + 1}/{MAX_RETRIES}): {e}")
                    time.sleep(delay)
                else:
                    print(f"❌ 请求失败，已达到最大重试次数：{e}")
        
        raise last_exception
    
    return wrapper

def tenacity_retry(func):
    """
    使用 tenacity 库的重试装饰器（更强大）
    """
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=BASE_DELAY, max=MAX_DELAY),
        retry=retry_if_exception_type((
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException
        )),
        reraise=True
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    return wrapper

# 使用示例
if __name__ == "__main__":
    @retry_request
    def fetch_url(url):
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    
    # 测试
    try:
        content = fetch_url("https://www.chinanews.com.cn/rss/finance.xml")
        print(f"✅ 成功获取 {len(content)} 字节")
    except Exception as e:
        print(f"❌ 最终失败：{e}")
