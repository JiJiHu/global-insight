from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
import os
from datetime import datetime, timezone, timedelta

app = FastAPI(title="Global Insight API Lite", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "150.40.177.181"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "global_insight"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )

@app.get("/api/v1/health")
def health():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM market_data")
        market_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM news")
        news_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {"status": "healthy", "market_count": market_count, "news_count": news_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market")
def get_market(limit: int = 10, type: Optional[str] = None):
    try:
        conn = get_db()
        cur = conn.cursor()
        if type:
            cur.execute("SELECT * FROM market_data WHERE type = %s ORDER BY created_at DESC LIMIT %s", (type, limit))
        else:
            cur.execute("SELECT * FROM market_data ORDER BY created_at DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"symbol": r[1], "price": r[2], "change": r[3], "type": r[4], "created_at": r[5]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/news")
def get_news(limit: int = 5):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM news ORDER BY created_at DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": r[0], "title": r[1], "summary": r[2], "url": r[3], "created_at": r[4]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
