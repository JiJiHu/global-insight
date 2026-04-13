"""
Global Insight API - 使用 Neon HTTP API（无需 psycopg2）
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import httpx
from urllib.parse import urlparse

app = FastAPI(title="Global Insight API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neon HTTP API 客户端
class NeonClient:
    def __init__(self):
        url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
        parsed = urlparse(url)
        self.host = parsed.hostname
        self.database = parsed.path.lstrip('/')
        self.user = parsed.username
        self.password = parsed.password
        self.api_url = f"https://{self.host}/v2/sql"
    
    def query(self, sql, params=None):
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                self.api_url,
                json={"sql": sql, "args": params or []},
                auth=(self.user, self.password)
            )
            response.raise_for_status()
            result = response.json()
            return result.get("rows", [])

neon = NeonClient()

@app.get("/api/v1/health")
def health_check():
    try:
        result = neon.query("SELECT 1 as test")
        return {"status": "healthy", "database": "connected", "test": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market")
def get_market_data(type: Optional[str] = None, limit: int = 100):
    try:
        if type:
            sql = """
                SELECT DISTINCT ON (symbol) symbol, price, change_percent, volume, timestamp, type
                FROM market_data WHERE type = %s ORDER BY symbol, timestamp DESC LIMIT %s
            """
            rows = neon.query(sql, [type, limit])
        else:
            sql = """
                SELECT DISTINCT ON (symbol) symbol, price, change_percent, volume, timestamp, type
                FROM market_data ORDER BY symbol, timestamp DESC LIMIT %s
            """
            rows = neon.query(sql, [limit])
        
        return [
            {
                "symbol": r[0], "price": float(r[1]), 
                "change_percent": float(r[2]) if r[2] else 0,
                "volume": int(r[3]) if r[3] else 0,
                "timestamp": r[4].isoformat() if r[4] else None,
                "type": r[5] if len(r) > 5 else 'stock'
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/news")
def get_news(limit: int = 50, source: Optional[str] = None):
    try:
        if source:
            sql = "SELECT * FROM news WHERE source ILIKE %s ORDER BY created_at DESC LIMIT %s"
            rows = neon.query(sql, [f"%{source}%", limit])
        else:
            sql = "SELECT * FROM news ORDER BY created_at DESC LIMIT %s"
            rows = neon.query(sql, [limit])
        
        return [
            {
                "id": r[0], "title": r[1], "content": r[2],
                "source": r[3], "url": r[4],
                "sentiment_label": r[5], "created_at": r[6].isoformat() if r[6] else None
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/insights")
def get_insights(limit: int = 10):
    try:
        sql = "SELECT * FROM ai_insights ORDER BY created_at DESC LIMIT %s"
        rows = neon.query(sql, [limit])
        
        return [
            {
                "id": r[0], "title": r[1], "content": r[2],
                "analysis_type": r[3], "confidence_score": float(r[4]) if r[4] else 0,
                "created_at": r[5].isoformat() if r[5] else None
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/graph")
def get_graph():
    try:
        nodes = neon.query("SELECT id, label, type, data FROM graph_nodes LIMIT 100")
        links = neon.query("SELECT source, target, type FROM graph_edges LIMIT 200")
        
        return {
            "nodes": [
                {"id": r[0], "label": r[1], "type": r[2], "data": r[3] or {}}
                for r in nodes
            ],
            "links": [
                {"source": r[0], "target": r[1], "type": r[2]}
                for r in links
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
