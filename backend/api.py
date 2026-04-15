from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import sys
from datetime import timezone, timedelta

# Vercel 环境检测和配置
IS_VERCEL = os.getenv("VERCEL") == "1"
if IS_VERCEL:
    # Vercel 环境：使用 config_vercel
    from config_vercel import DATABASE_URL
    print(f"[DEBUG] Running on Vercel, DATABASE_URL={DATABASE_URL[:50]}...", file=sys.stderr)
else:
    # 本地环境：使用 config
    from config import DATABASE_URL
    print(f"[DEBUG] Running locally, DATABASE_URL={DATABASE_URL[:50]}...", file=sys.stderr)

from db import get_db_connection
from utils.cache import cached, api_cache

app = FastAPI(title="Finance Insight API", version="1.1.0")

# 导入 Vercel Cron 路由
try:
    from vercel_cron import router as cron_router
    app.include_router(cron_router)
except ImportError:
    pass  # 本地开发时可能没有这个模块

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/test")
def test_endpoint():
    """简单测试端点 - 不依赖数据库"""
    import sys
    print("[DEBUG] Test endpoint called", file=sys.stderr)
    return {
        "status": "ok",
        "vercel": IS_VERCEL,
        "python_version": sys.version,
        "env_vars": {
            "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
            "POSTGRES_URL": bool(os.getenv("POSTGRES_URL")),
        }
    }

@app.get("/api/v1/health")
def health_check():
    """健康检查端点"""
    import sys
    try:
        from datetime import datetime
        
        # 调试信息
        print(f"[DEBUG] IS_VERCEL={IS_VERCEL}", file=sys.stderr)
        print(f"[DEBUG] DATABASE_URL exists={bool(DATABASE_URL)}", file=sys.stderr)
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # 检查数据库连接
            cur.execute("SELECT 1")
            
            # 检查数据量
            cur.execute("SELECT COUNT(*) FROM news")
            news_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM market_data")
            market_count = cur.fetchone()[0]
            
            cur.execute("SELECT MAX(created_at) FROM news")
            latest_news = cur.fetchone()[0]
            
            cur.close()
        
        # 检查数据是否新鲜（最新新闻是否在 24 小时内）
        data_fresh = False
        if latest_news:
            from datetime import timedelta, timezone
            # 处理时区问题
            now = datetime.now(timezone.utc)
            if latest_news.tzinfo is None:
                latest_news = latest_news.replace(tzinfo=timezone.utc)
            data_fresh = latest_news > (now - timedelta(hours=24))
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "news_count": news_count,
                "market_count": market_count,
                "latest_news": latest_news.isoformat() if latest_news else None,
                "data_fresh": data_fresh
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/api/v1/market")
def get_all_market(type: str = None):
    """获取市场行情数据，支持按类型筛选：stock, gold, oil"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        if type:
            cur.execute("""
                SELECT DISTINCT ON (symbol)
                    symbol, price, change_percent, volume, timestamp, type
                FROM market_data
                WHERE type = %s
                ORDER BY symbol, timestamp DESC
            """, (type,))
        else:
            cur.execute("""
                SELECT DISTINCT ON (symbol)
                    symbol, price, change_percent, volume, timestamp, type
                FROM market_data
                ORDER BY symbol, timestamp DESC
            """)
        results = cur.fetchall()
        cur.close()
        
        # 北京时间时区 (UTC+8)
        bj_tz = timezone(timedelta(hours=8))
        
        return [
            {
                "symbol": r[0],
                "price": float(r[1]),
                "change_percent": float(r[2]) if r[2] else 0,
                "volume": int(r[3]) if r[3] else 0,
                "timestamp": r[4].astimezone(bj_tz).isoformat() if r[4] else None,
                "type": r[5] if len(r) > 5 else 'stock'
            }
            for r in results
        ]

@app.get("/api/v1/market/types")
def get_market_types():
    """获取所有市场数据类型统计"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT type, COUNT(DISTINCT symbol) as count
            FROM market_data
            GROUP BY type
        """)
        results = cur.fetchall()
        cur.close()
        
        return {
            r[0]: r[1] for r in results
        }

@app.get("/api/v1/stats")
def get_stats():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM market_data")
        market_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM news")
        news_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT symbol) FROM market_data")
        symbol_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT source) FROM news")
        source_count = cur.fetchone()[0]
        
        # 按类型统计
        cur.execute("""
            SELECT type, COUNT(DISTINCT symbol) as count
            FROM market_data
            GROUP BY type
        """)
        type_stats = {r[0]: r[1] for r in cur.fetchall()}
        cur.close()
        
        return {
            "market_data_count": market_count,
            "news_count": news_count,
            "unique_symbols": symbol_count,
            "news_sources": source_count,
            "type_stats": type_stats,
            "stock_count": type_stats.get('stock', 0),
            "gold_count": type_stats.get('gold', 0),
            "oil_count": type_stats.get('oil', 0),
            "crypto_count": type_stats.get('crypto', 0)
        }

@app.get("/api/v1/news")
@cached(ttl=180)  # 缓存 3 分钟
def get_news(limit: int = 100, offset: int = 0, source: str = None):
    """获取新闻数据（支持分页和按来源筛选）"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        if source:
            # 按来源模糊匹配
            cur.execute("""
                SELECT id, title, content, source, sentiment_label, created_at, url
                FROM news
                WHERE source LIKE %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (f'%{source}%', limit, offset))
        else:
            cur.execute("""
                SELECT id, title, content, source, sentiment_label, created_at, url
                FROM news
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
        results = cur.fetchall()
        cur.close()
        
        # 北京时间时区 (UTC+8)
        bj_tz = timezone(timedelta(hours=8))
        
        return [
            {
                "id": r[0],
                "title": r[1],
                "content": r[2] or "暂无详细内容",
                "source": r[3],
                "sentiment": r[4],
                "published_at": r[5].astimezone(bj_tz).isoformat() if r[5] else None,
                "url": r[6]
            }
            for r in results
        ]

@app.get("/api/v1/insights")
def get_insights(limit: int = 10):
    """获取AI洞察数据"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, content, confidence_score, analysis_type, created_at
            FROM insights
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        results = cur.fetchall()
        cur.close()
        
        # 北京时间时区 (UTC+8)
        bj_tz = timezone(timedelta(hours=8))
        
        return [
            {
                "id": r[0],
                "title": r[1],
                "content": r[2],
                "confidence_score": float(r[3]) if r[3] else 0,
                "analysis_type": r[4],
                "created_at": r[5].astimezone(bj_tz).isoformat() if r[5] else None,
                "source": "AI",  # AI 生成的洞察
                "url": "",  # AI 洞察暂无原文链接
            }
            for r in results
        ]

@app.get("/api/v1/graph")
def get_graph():
    """获取金融知识图谱数据（从预生成的 JSON 文件加载）"""
    import os
    import json
    
    graph_file = '/app/graph_data.json'
    
    # 如果图谱文件存在，直接加载
    if os.path.exists(graph_file):
        try:
            with open(graph_file, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            return graph_data
        except Exception as e:
            print(f"⚠️ 加载图谱文件失败：{e}")
    
    # 否则使用旧的动态生成逻辑
    with get_db_connection() as conn:
        cur = conn.cursor()
        # 获取股票作为节点
        cur.execute("""
            SELECT DISTINCT symbol FROM market_data LIMIT 50
        """)
        symbols = cur.fetchall()
        
        # 获取新闻源作为节点
        cur.execute("""
            SELECT DISTINCT source FROM news WHERE source IS NOT NULL LIMIT 20
        """)
        sources = cur.fetchall()
        cur.close()
        
        nodes = []
        edges = []
        
        # 添加股票节点
        for i, s in enumerate(symbols):
            nodes.append({
                "id": f"stock_{i}",
                "name": s[0],
                "type": "stock",
                "properties": {}
            })
        
        # 添加新闻源节点
        for i, s in enumerate(sources):
            nodes.append({
                "id": f"source_{i}",
                "name": s[0],
                "type": "source",
                "properties": {}
            })
        
        # 生成一些边（股票和新闻源之间的关系）
        for i in range(min(len(symbols), len(sources))):
            edges.append({
                "id": f"edge_{i}",
                "source": f"stock_{i}",
                "target": f"source_{i % len(sources)}",
                "relation": "mentioned",
                "weight": 1.0
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
