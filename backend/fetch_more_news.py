#!/usr/bin/env python3
"""
获取更多新闻源的数据
- Finnhub (财经新闻 API)
- Reuters (路透社 RSS)
- GitHub (开发者新闻)
"""
import sys
sys.path.insert(0, '/app')
from db import get_db_connection
from config import FINNHUB_API_KEY
import feedparser
import requests
from datetime import datetime, timezone

# 新闻源配置
NEWS_SOURCES = {
    'Finnhub': {
        'type': 'api',
        'url': 'https://finnhub.io/api/v1/news',
        'params': {'category': 'general', 'token': FINNHUB_API_KEY}
    },
    'Reuters': {
        'type': 'rss',
        'url': 'https://feeds.reuters.com/reuters/topNews'
    },
    'GitHub': {
        'type': 'rss',
        'url': 'https://github.blog/feed/'
    },
    '华尔街见闻': {
        'type': 'rss',
        'url': 'https://wallstreetcn.com/feed'
    }
}

def fetch_finnhub_news(limit=20):
    """从 Google News RSS 获取财经新闻（替代 Finnhub API）"""
    print("📈 获取财经新闻 (Google News)...）")
    news_list = []
    
    try:
        # 使用 Google News 财经 RSS
        feed = feedparser.parse('https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZ4ZG1Gc0lCQ0NqSmdvQWFnQg?hl=zh-CN&gl=CN&ceid=CN:zh-CN')
        
        for entry in feed.entries[:limit]:
            title = entry.title
            url = entry.link
            published = entry.published if hasattr(entry, 'published') else ''
            
            news_item = {
                'title': title,
                'url': url,
                'source': 'Finnhub',
                'published_at': published,
                'content': title,
                'sentiment': '中性'
            }
            news_list.append(news_item)
    except Exception as e:
        print(f"   ❌ Google News 失败：{e}")
    
    print(f"   ✅ 获取 {len(news_list)} 条")
    return news_list

def fetch_rss_news(source_name, url, limit=10):
    """从 RSS 源获取新闻"""
    print(f"📰 获取 {source_name} 新闻...")
    news_list = []
    
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_at = datetime.fromtimestamp(entry.published_parsed.mktime()).isoformat()
                except:
                    published_at = datetime.now().isoformat()
            
            news_item = {
                'title': entry.title,
                'url': entry.link,
                'source': source_name,
                'published_at': published_at,
                'content': entry.summary[:500] if hasattr(entry, 'summary') else entry.title,
                'sentiment': '中性'
            }
            news_list.append(news_item)
    except Exception as e:
        print(f"   ❌ {source_name} 失败：{e}")
    
    print(f"   ✅ 获取 {len(news_list)} 条")
    return news_list

def save_to_database(news_list):
    """保存新闻到数据库"""
    if not news_list:
        return 0
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        saved = 0
        
        for news in news_list:
            try:
                # 检查是否已存在
                cur.execute("SELECT id FROM news WHERE url = %s", (news['url'],))
                if cur.fetchone():
                    continue
                
                # 插入新闻
                cur.execute("""
                    INSERT INTO news (title, content, source, sentiment_label, url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    news['title'],
                    news['content'],
                    news['source'],
                    news['sentiment'],
                    news['url'],
                    news['published_at']
                ))
                saved += 1
                
            except Exception as e:
                print(f"⚠️ 保存失败：{e}")
        
        conn.commit()
        cur.close()
    
    return saved

if __name__ == "__main__":
    all_news = []
    
    # 获取各源新闻
    all_news.extend(fetch_finnhub_news())
    all_news.extend(fetch_rss_news('Reuters', NEWS_SOURCES['Reuters']['url']))
    all_news.extend(fetch_rss_news('GitHub', NEWS_SOURCES['GitHub']['url']))
    all_news.extend(fetch_rss_news('华尔街见闻', NEWS_SOURCES['华尔街见闻']['url']))
    
    # 保存到数据库
    saved = save_to_database(all_news)
    print(f"\n💾 保存 {saved} 条新新闻到数据库")
