from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from db import get_db_connection
import json
import os

app = FastAPI(title="Finance Insight API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/v1/market")
def get_all_market():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT ON (symbol)
                symbol, price, change_percent, volume, timestamp
            FROM market_data
            ORDER BY symbol, timestamp DESC
        """)
        results = cur.fetchall()
        cur.close()
        
        return [
            {
                "symbol": r[0],
                "price": float(r[1]),
                "change_percent": float(r[2]) if r[2] else 0,
                "volume": int(r[3]) if r[3] else 0,
                "timestamp": r[4].isoformat() if r[4] else None
            }
            for r in results
        ]

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
        cur.close()
        
        return {
            "market_data_count": market_count,
            "news_count": news_count,
            "unique_symbols": symbol_count,
            "news_sources": source_count
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
