# 极简 FastAPI 应用 - 测试 Vercel 环境
from fastapi import FastAPI
import sys
import os

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "python": sys.version}

@app.get("/env")
def env_check():
    return {
        "vercel": os.getenv("VERCEL"),
        "database_url": bool(os.getenv("DATABASE_URL")),
        "path": sys.path[:3]
    }
