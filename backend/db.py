"""
PostgreSQL 数据库连接和工具函数
"""
import psycopg2
from pgvector.psycopg2 import register_vector
from contextlib import contextmanager
import os

# 从环境变量读取数据库 URL
DATABASE_URL = os.getenv("DATABASE_URL")

# 默认值（本地开发）
if not DATABASE_URL:
    try:
        from config import DATABASE_URL as LOCAL_DB_URL
        DATABASE_URL = LOCAL_DB_URL
    except:
        DATABASE_URL = "postgresql://jack:ChangeMe123!@localhost:5432/finance_insight"

@contextmanager
def get_db_connection():
    """获取数据库连接上下文管理器"""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        register_vector(conn)
        yield conn
    finally:
        if conn:
            conn.close()

def insert_market_data(symbol, type_, price, change_percent, volume=None):
    """插入金融数据"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO market_data (symbol, type, price, change_percent, volume)
            VALUES (%s, %s, %s, %s, %s)
        """, (symbol, type_, price, change_percent, volume))
        conn.commit()
        cur.close()

def insert_news(title, content, source, url=None, sentiment_score=None, 
                sentiment_label=None, embedding=None, related_symbols=None):
    """插入新闻数据"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO news (title, content, source, url, sentiment_score, 
                            sentiment_label, embedding, related_symbols)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, content, source, url, sentiment_score, sentiment_label, 
              embedding, related_symbols))
        conn.commit()
        cur.close()

def search_news_by_symbol(symbol, limit=10):
    """根据标的搜索新闻"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT title, source, sentiment_score, created_at
            FROM news
            WHERE related_symbols @> ARRAY[%s]
            ORDER BY created_at DESC
            LIMIT %s
        """, (symbol, limit))
        results = cur.fetchall()
        cur.close()
        return results

def search_news_by_embedding(query_embedding, limit=10):
    """向量相似度搜索"""
    import numpy as np
    with get_db_connection() as conn:
        cur = conn.cursor()
        # 确保是 numpy 数组格式
        if isinstance(query_embedding, list):
            query_embedding = np.array(query_embedding, dtype=np.float32)
        cur.execute("""
            SELECT title, content, sentiment_score
            FROM news
            ORDER BY embedding <-> %s
            LIMIT %s
        """, (query_embedding, limit))
        results = cur.fetchall()
        cur.close()
        return results

def get_latest_market_data(symbol):
    """获取最新行情数据"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT symbol, price, change_percent, volume, timestamp
            FROM market_data
            WHERE symbol = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (symbol,))
        result = cur.fetchone()
        cur.close()
        return result

if __name__ == "__main__":
    # 测试连接
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT version()")
            print("✅ 数据库连接成功!")
            print(cur.fetchone()[0])
            cur.close()
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
