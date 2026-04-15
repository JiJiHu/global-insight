#!/usr/bin/env python3
"""
简化的新闻抓取脚本 - 直接在 Railway 上运行
不依赖复杂模块，只使用 requests 和 psycopg2
"""
import requests
from datetime import datetime, timedelta, timezone
import psycopg2
import os

# 北京时间
BEIJING_TZ = timezone(timedelta(hours=8))

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    exit(1)

# Finnhub API
FINNHUB_API_KEY = "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"

def simple_sentiment(text):
    """简单情感分析"""
    text_lower = text.lower()
    if any(word in text_lower for word in ['rise', 'gain', 'grow', 'surge', 'beat', 'strong', 'positive', 'up']):
        return 0.6, '积极'
    elif any(word in text_lower for word in ['fall', 'drop', 'decline', 'crash', 'miss', 'weak', 'negative', 'down']):
        return -0.6, '消极'
    return 0.0, '中性'

def fetch_news():
    """抓取新闻并保存到数据库"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取新闻...")
    
    params = {
        'token': FINNHUB_API_KEY,
        'category': 'general',
        'from': int((datetime.now() - timedelta(days=7)).timestamp()),
        'to': int(datetime.now().timestamp())
    }
    
    try:
        response = requests.get('https://finnhub.io/api/v1/news', params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, list):
            print(f"❌ API 返回错误：{data}")
            return 0
        
        print(f"✅ 获取到 {len(data)} 条新闻")
        
        # 连接数据库
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        saved = 0
        for item in data[:30]:  # 最多 30 条
            title = item.get('headline', '')
            summary = item.get('summary', '') or title
            url = item.get('url', '')
            published = item.get('datetime', 0)
            source = item.get('source', 'Finnhub')
            
            if not title:
                continue
            
            sentiment_score, sentiment_label = simple_sentiment(title + ' ' + summary)
            
            try:
                cur.execute("""
                    INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, published_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (title) DO NOTHING
                """, (title, summary, source, sentiment_label, sentiment_score, url, 
                      datetime.fromtimestamp(published, tz=BEIJING_TZ)))
                saved += 1
            except Exception as e:
                print(f"  保存失败：{e}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ 成功保存 {saved} 条新闻")
        return saved
        
    except Exception as e:
        print(f"❌ 新闻抓取失败：{e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    fetch_news()
