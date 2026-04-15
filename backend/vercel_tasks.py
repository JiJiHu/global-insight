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

def simple_sentiment(text):
    """简单情感分析"""
    if not text:
        return 0.0, '中性'
    
    text_lower = text.lower()
    
    positive = ['涨', '上涨', '增长', '利好', '强劲', '突破', '新高', '上升', '反弹',
               'rise', 'gain', 'grow', 'surge', 'jump', 'beat', 'record', 'strong', 'positive', 'up', 'rally']
    negative = ['跌', '下跌', '跌幅', '负面', '下滑', '暴跌', '崩盘', '危机',
               'fall', 'drop', 'decline', 'crash', 'plunge', 'miss', 'weak', 'negative', 'down', 'loss', 'tumble']
    
    pos_count = sum(1 for word in positive if word in text_lower)
    neg_count = sum(1 for word in negative if word in text_lower)
    
    if pos_count > neg_count:
        return 0.6, '积极'
    elif neg_count > pos_count:
        return -0.6, '消极'
    else:
        return 0.0, '中性'


def fetch_news():
    """抓取新闻并写入数据库（多源版本）"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取新闻...")
    
    total_saved = 0
    
    # 1. Finnhub 新闻 API
    try:
        response = requests.get("https://finnhub.io/api/v1/news", params={
            "category": "general",
            "token": "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"
        }, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f" ✅ Finnhub 获取到 {len(data)} 条新闻")
                saved = save_news_batch(data, "Finnhub")
                total_saved += saved
                print(f"    保存了 {saved} 条 Finnhub 新闻")
    except Exception as e:
        print(f" ❌ Finnhub 抓取失败：{e}")
    
    # 2. 尝试从 fetch_news_sources 导入更多新闻源
    try:
        from fetch_news_sources import fetch_all_sources
        try:
            sources_saved = fetch_all_sources()
            total_saved += sources_saved
            print(f" ✅ 其他来源保存了 {sources_saved} 条新闻")
        except Exception as e:
            print(f" ⚠️ fetch_news_sources 执行失败：{e}")
    except ImportError:
        print(" ⚠️ fetch_news_sources 模块不可用，仅使用 Finnhub")
    except Exception as e:
        print(f" ⚠️ 导入失败：{e}")
    
    print(f"\n📊 新闻抓取完成！共保存 {total_saved} 条新闻")
    return total_saved


def save_news_batch(data, default_source="Finnhub"):
    """批量保存新闻到数据库"""
    saved = 0
    skipped = 0
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        for item in data[:100]:
            title = item.get('headline') or item.get('title') or item.get('text', '')
            summary = item.get('summary') or item.get('description') or item.get('content', '')
            url = item.get('url', '')
            published = item.get('datetime') or item.get('published_at')
            source = item.get('source', default_source)
            
            if not title:
                continue
            
            # 处理时间戳
            if isinstance(published, (int, float)):
                published = datetime.fromtimestamp(published, tz=BEIJING_TZ)
            elif isinstance(published, str):
                try:
                    published = datetime.fromisoformat(published.replace('Z', '+00:00'))
                except:
                    published = datetime.now(BEIJING_TZ)
            else:
                published = datetime.now(BEIJING_TZ)
            
            # 简单情感分析
            sentiment_score, sentiment_label = simple_sentiment(title + ' ' + summary)
            
            # 检查 URL 是否已存在
            try:
                cur.execute("SELECT id FROM news WHERE url = %s LIMIT 1", (url,))
                if cur.fetchone():
                    skipped += 1
                    continue
            except:
                pass
            
            # 插入数据库
            try:
                cur.execute("""
                    INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    title[:500] if title else '',
                    summary[:2000] if summary else '',
                    source,
                    sentiment_label,
                    sentiment_score,
                    url,
                    published
                ))
                saved += 1
            except:
                continue
        
        conn.commit()
        cur.close()
    
    return saved


def generate_insights():
    """生成 AI 洞察（简化版）"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始生成 AI 洞察...")
    
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    if not DASHSCOPE_API_KEY:
        print(" ⚠️ 缺少 DASHSCOPE_API_KEY，跳过 AI 洞察生成")
        return 0
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
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
                return 0
            
            insight_title = f"📊 市场快报 - {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M')}"
            insight_content = "今日市场动态：\n"
            
            for symbol, type_, price, change in markets[:10]:
                if change:
                    trend = "📈" if change > 0 else "📉"
                    insight_content += f"{trend} {symbol}: ${price:.2f} ({change:+.2f}%)\n"
            
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
        
        print(" ✅ AI 洞察生成成功")
        return 1
        
    except Exception as e:
        print(f" ❌ AI 洞察生成失败：{e}")
        return 0


def build_graph():
    """构建知识图谱（简化版）"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始构建知识图谱...")
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("SELECT DISTINCT type FROM market_data")
            types = [row[0] for row in cur.fetchall()]
            
            nodes = []
            links = []
            
            nodes.append({"id": "market", "label": "金融市场", "type": "center"})
            
            for type_ in types:
                nodes.append({"id": type_, "label": type_.upper(), "type": "category"})
                links.append({"source": "market", "target": type_})
                
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
        
        print(f" ✅ 知识图谱构建完成：{len(nodes)} 个节点，{len(links)} 条边")
        return {'nodes': nodes, 'links': links}
        
    except Exception as e:
        print(f" ❌ 知识图谱构建失败：{e}")
        return {'nodes': [], 'links': []}
