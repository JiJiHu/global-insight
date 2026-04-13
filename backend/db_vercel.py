"""
使用 Vercel Postgres 集成的数据库模块
"""
import os
import httpx

# Vercel Postgres 通过 HTTP API 访问
VERCEL_POSTGRES_URL = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")

class VercelDB:
    """Vercel Postgres 数据库客户端"""
    
    def __init__(self):
        self.url = VERCEL_POSTGRES_URL
    
    async def query(self, sql, params=None):
        """执行 SQL 查询"""
        async with httpx.AsyncClient() as client:
            # Vercel Postgres HTTP API
            response = await client.post(
                "https://api.vercel.com/v1/postgres/query",
                json={
                    "query": sql,
                    "params": params or []
                },
                headers={
                    "Authorization": f"Bearer {os.getenv('VERCEL_TOKEN')}"
                }
            )
            return response.json()

# 保持原有接口兼容
def get_db_connection():
    """返回一个简单的连接对象"""
    return VercelDB()
