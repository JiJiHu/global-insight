"""
Neon HTTP API 客户端 - 无需 psycopg2
"""
import os
import httpx
from urllib.parse import urlparse, parse_qs

class NeonHTTPClient:
    """使用 Neon 的 HTTP API 连接数据库"""
    
    def __init__(self):
        # 解析连接字符串
        url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
        parsed = urlparse(url)
        
        self.host = parsed.hostname
        self.database = parsed.path.lstrip('/')
        self.user = parsed.username
        self.password = parsed.password
        
        # Neon HTTP API 端点
        self.api_url = f"https://{self.host}/v2/sql"
    
    async def execute(self, query, params=None):
        """执行 SQL 查询"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json={
                    "sql": query,
                    "args": params or []
                },
                auth=(self.user, self.password)
            )
            response.raise_for_status()
            return response.json()
    
    def execute_sync(self, query, params=None):
        """同步执行 SQL 查询"""
        with httpx.Client() as client:
            response = client.post(
                self.api_url,
                json={
                    "sql": query,
                    "args": params or []
                },
                auth=(self.user, self.password)
            )
            response.raise_for_status()
            return response.json()

# 全局客户端
neon_client = NeonHTTPClient()

def get_db_connection():
    """返回 Neon HTTP 客户端"""
    return neon_client
