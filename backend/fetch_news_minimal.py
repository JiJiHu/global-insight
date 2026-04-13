#!/usr/bin/env python3
"""
极简新闻抓取 - 只使用 requests
从 Finnhub 获取新闻并保存
"""
import requests
from datetime import datetime, timedelta
from db import get_db_connection
import time

API_KEY = "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"

def simple_sentiment(text):
    """简单情感分析"""
    text = text.lower()
    positive = ['rise', 'gain', 'grow', 'surge', 'jump', 'beat', 'record', 'strong', 'positive', 'up']
    negative = ['fall', 'drop', 'decline', 'crash', 'plunge', 'miss', 'weak', 'negative', 'down', 'loss']
    
    score = sum(1 for word in positive if word in text) - sum(1 for word in negative if word in text)
    if score > 0:
        return 0.6, 'positive'
    elif score < 0:
        return -0.6, 'negative'
    else:
        return 0.0, 'neutral'

def fetch_news():
    """抓取新闻"""
    print(f"📰 开始抓取新闻 - {datetime.now()}")
    print("=" * 60)
    
    params = {
        'token': API_KEY,
        'category': 'general',
        'from': int((datetime.now() - timedelta(days=7)).timestamp()),
        'to': int(datetime.now().timestamp())
    }
    
    try:
        response = requests.get('https://finnhub.io/api/v1/news', params=params, timeout=15)
        data = response.json()
        
        if not isinstance(data, list):
            print(f"❌ API 返回错误：{data}")
            return 0
        
        print(f"✅ 获取到 {len(data)} 条新闻")
        
        # 保存到数据库
        saved = 0
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            for item in data[:30]:  # 最多保存 30 条
                title = item.get('headline', '')
                summary = item.get('summary', '')
                url = item.get('url', '')
                published = item.get('datetime', 0)
                
                if not title:
                    continue
                
                # 检查是否已存在
                cur.execute("SELECT id FROM news WHERE title = %s", (title,))
                if cur.fetchone():
                    continue
                
                # 如果 summary 为空，使用 title 作为 content
                if not summary or len(summary.strip()) == 0:
                    summary = title  # 至少要有标题作为内容
                
                # 情感分析
                score, label = simple_sentiment(title + " " + summary)
                
                # 插入数据库
                cur.execute("""
                    INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    title,
                    summary,
                    'Finnhub',
                    label,
                    score,
                    url,
                    datetime.fromtimestamp(published)
                ))
                saved += 1
            
            conn.commit()
            cur.close()
        
        print(f"✅ 成功保存 {saved} 条新闻")
        
        # 统计
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM news")
            total = cur.fetchone()[0]
            cur.execute("SELECT MAX(created_at) FROM news")
            latest = cur.fetchone()[0]
            print(f"📊 新闻总数：{total}")
            print(f"🕒 最新新闻：{latest}")
            cur.close()
        
        return saved
        
    except Exception as e:
        print(f"❌ 抓取失败：{e}")
        return 0

if __name__ == "__main__":
    fetch_news()
