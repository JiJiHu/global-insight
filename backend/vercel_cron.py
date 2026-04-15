"""
Vercel Cron Jobs 端点
这些端点由 Vercel Cron 定时调用，触发数据抓取和 AI 生成任务
"""

from fastapi import APIRouter, HTTPException
import subprocess
import os

router = APIRouter()

@router.get("/api/v1/cron/fetch-market")
def cron_fetch_market():
    """
    定时任务：抓取市场数据
     schedule: 0 */6 * * * (每 6 小时)
    """
    try:
        # 在 Vercel Serverless 环境中，直接调用 Python 脚本
        from fetch_market_data import fetch_all_market_data
        from fetch_commodities import fetch_all
        
        # 抓取美股
        fetch_all_market_data()
        
        # 抓取大宗商品
        fetch_all()
        
        return {
            "status": "success",
            "message": "Market data fetched successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/cron/fetch-news")
def cron_fetch_news():
    """
    定时任务：抓取新闻
    schedule: 0 8 * * * (每天 8 点)
    """
    try:
        from vercel_tasks import fetch_news
        
        count = fetch_news()
        
        return {
            "status": "success",
            "message": f"News fetched successfully: {count} articles",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/cron/generate-insights")
def cron_generate_insights():
    """
    定时任务：生成 AI 洞察
    schedule: 0 9 * * * (每天 9 点)
    """
    try:
        from vercel_tasks import generate_insights
        
        count = generate_insights()
        
        return {
            "status": "success",
            "message": f"AI insights generated: {count} insights",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/cron/build-graph")
def cron_build_graph():
    """
    定时任务：构建知识图谱
    schedule: 0 10 * * * (每天 10 点)
    """
    try:
        from vercel_tasks import build_graph
        
        graph = build_graph()
        
        return {
            "status": "success",
            "message": f"Knowledge graph built: {len(graph.get('nodes', []))} nodes, {len(graph.get('links', []))} edges",
            "graph": graph
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
