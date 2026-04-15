#!/usr/bin/env python3
"""
Vercel Serverless 专用任务 - 使用原生 SQL，不依赖 ORM
"""
import os
import requests
from datetime import datetime, timezone, timedelta
from db import get_db_connection

# 北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

def fetch_news():
    """抓取新闻并写入数据库（使用原生 SQL）"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取新闻...")
    
    try:
        # 使用 Finnhub 新闻 API
        response = requests.get("https://finnhub.io/api/v1/news", params={
            "category": "general",
            "token": "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"
        }, timeout=10)
        
        if response.status_code != 200:
            print(f" ❌ 新闻 API 请求失败：{response.status_code}")
            return 0
        
        data = response.json()
        if not isinstance(data, list):
            print(f" ❌ API 返回错误：{data}")
            return 0
        
        print(f" ✅ 获取到 {len(data)} 条新闻")
        
        # 保存到数据库
        conn = get_db_connection()
        cur = conn.cursor()
        saved = 0
        skipped = 0
        
        for item in data[:50]:  # 最多保存 50 条
            title = item.get('headline', '')
            summary = item.get('summary', '') or title
            url = item.get('url', '')
            published = item.get('datetime', 0)
            source = item.get('source', 'Finnhub')
            
            if not title:
                continue
            
            # 简单情感分析
            sentiment_score = 0.0
            sentiment_label = '中性'
            text_lower = (title + ' ' + summary).lower()
            
            if any(word in text_lower for word in ['rise', 'gain', 'grow', 'surge', 'beat', 'strong', 'positive', 'up']):
                sentiment_score = 0.6
                sentiment_label = '积极'
            elif any(word in text_lower for word in ['fall', 'drop', 'decline', 'crash', 'miss', 'weak', 'negative', 'down']):
                sentiment_score = -0.6
                sentiment_label = '消极'
            
            # 检查 URL 是否已存在
            try:
                cur.execute("SELECT id FROM news WHERE url = %s LIMIT 1", (url,))
                if cur.fetchone():
                    skipped += 1
                    continue
            except Exception as e:
                print(f" ⚠️ 查询失败：{e}")
                conn.rollback()
                continue
            
            # 插入数据库（使用原生 SQL）
            try:
                cur.execute("""
                    INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    title,
                    summary,
                    source,
                    sentiment_label,
                    sentiment_score,
                    url,
                    datetime.fromtimestamp(published, tz=BEIJING_TZ) if published else datetime.now(BEIJING_TZ)
                ))
                saved += 1
            except Exception as e:
                print(f" ⚠️ 保存新闻失败：{e}")
                print(f"     标题：{title[:50]}...")
                print(f"     URL: {url[:80]}...")
                conn.rollback()
                continue
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f" ✅ 成功保存 {saved} 条新闻，跳过 {skipped} 条重复新闻")
        
        print(f" ✅ 成功保存 {saved} 条新闻")
        return saved
        
    except Exception as e:
        print(f" ❌ 新闻抓取失败：{e}")
        import traceback
        traceback.print_exc()
        return 0


def generate_insights():
    """生成 AI 洞察（简化版）"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始生成 AI 洞察...")
    
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    if not DASHSCOPE_API_KEY:
        print(" ⚠️ 缺少 DASHSCOPE_API_KEY，跳过 AI 洞察生成")
        return 0
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 获取最新市场数据
        cur.execute("""
            SELECT symbol, type, price, change_percent 
            FROM market_data 
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            ORDER BY timestamp DESC
        """)
        markets = cur.fetchall()
        
        if not markets:
            print(" ⚠️ 没有足够的市场数据生成洞察")
            cur.close()
            conn.close()
            return 0
        
        # 生成简单洞察
        insight_title = f"📊 市场快报 - {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M')}"
        insight_content = "今日市场动态：\n"
        
        for symbol, type_, price, change in markets[:10]:
            if change:
                trend = "📈" if change > 0 else "📉"
                insight_content += f"{trend} {symbol}: ${price:.2f} ({change:+.2f}%)\n"
        
        # 插入数据库
        cur.execute("""
            INSERT INTO insights (title, content, analysis_type, confidence_score, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            insight_title,
            insight_content,
            'market_summary',
            0.85,
            datetime.now(BEIJING_TZ)
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(" ✅ AI 洞察生成成功")
        return 1
        
    except Exception as e:
        print(f" ❌ AI 洞察生成失败：{e}")
        return 0


def build_graph():
    """构建知识图谱（简化版）"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始构建知识图谱...")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 获取所有资产类型
        cur.execute("SELECT DISTINCT type FROM market_data")
        types = [row[0] for row in cur.fetchall()]
        
        nodes = []
        links = []
        
        # 添加中心节点
        nodes.append({"id": "market", "label": "金融市场", "type": "center"})
        
        for type_ in types:
            # 添加类型节点
            nodes.append({"id": type_, "label": type_.upper(), "type": "category"})
            links.append({"source": "market", "target": type_})
            
            # 获取该类型的前 5 个资产
            cur.execute("""
                SELECT symbol, price, change_percent 
                FROM market_data 
                WHERE type = %s 
                ORDER BY timestamp DESC 
                LIMIT 5
            """, (type_,))
            
            assets = cur.fetchall()
            for symbol, price, change in assets:
                nodes.append({
                    "id": symbol,
                    "label": symbol,
                    "type": "asset",
                    "price": float(price) if price else 0,
                    "change": float(change) if change else 0
                })
                links.append({"source": type_, "target": symbol})
        
        cur.close()
        conn.close()
        
        print(f" ✅ 知识图谱构建完成：{len(nodes)} 个节点，{len(links)} 条边")
        return {'nodes': nodes, 'links': links}
        
    except Exception as e:
        print(f" ❌ 知识图谱构建失败：{e}")
        return {'nodes': [], 'links': []}
