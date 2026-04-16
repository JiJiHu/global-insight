#!/usr/bin/env python3
"""
Railway 定时任务 - 抓取所有新闻源并写入 Neon 数据库
每 30 分钟执行一次
"""
import os
import sys
import feedparser
import requests
from datetime import datetime, timezone

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
FINNHUB_API_KEY = "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not set!")
    sys.exit(1)

print(f"✅ DATABASE_URL configured")
print(f"🕐 当前时间：{datetime.now(timezone.utc).isoformat()}")

# 使用 psycopg2 直接插入
import psycopg2

def insert_news(title, content, source, url, created_at):
    """插入新闻到数据库"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO news (title, content, source, url, created_at) VALUES (%s, %s, %s, %s, %s)",
            (title[:500], content[:2000], source, url[:500], created_at)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ 插入失败：{e}")
        return False

def fetch_finnhub_news():
    """抓取 Finnhub 新闻"""
    print("\n📰 Finnhub API...")
    try:
        url = f"https://api.finnhub.io/api/v1/news?category=general&token={FINNHUB_API_KEY}"
        resp = requests.get(url, timeout=30)
        data = resp.json()
        print(f"   获取到 {len(data)} 条")
        
        count = 0
        for news in data:
            title = news.get('headline', '')
            summary = news.get('summary', '')
            source = news.get('source', 'Finnhub')
            url = news.get('url', '')
            ts = datetime.fromtimestamp(news.get('datetime', 0), tz=timezone.utc).isoformat()
            
            if insert_news(title, summary, source, url, ts):
                count += 1
        
        print(f"   ✅ 插入 {count} 条")
        return count
    except Exception as e:
        print(f"   ❌ 错误：{e}")
        return 0

def fetch_rss_news(name, url):
    """抓取 RSS 新闻"""
    print(f"\n📰 {name}...")
    try:
        feed = feedparser.parse(url)
        print(f"   获取到 {len(feed.entries)} 条")
        
        count = 0
        for entry in feed.entries[:30]:
            title = entry.title
            summary = entry.get('description', entry.get('summary', ''))
            link = entry.get('link', '')
            pub_date = entry.get('published', '')
            
            try:
                dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                ts = dt.isoformat()
            except:
                ts = datetime.now(timezone.utc).isoformat()
            
            if insert_news(title, summary, name, link, ts):
                count += 1
        
        print(f"   ✅ 插入 {count} 条")
        return count
    except Exception as e:
        print(f"   ❌ 错误：{e}")
        return 0

def fetch_twitter_nitter(account):
    """通过 Nitter 抓取 Twitter"""
    print(f"\n🐦 Twitter: @{account}...")
    try:
        rss_url = f'https://nitter.net/{account}/rss'
        feed = feedparser.parse(rss_url)
        print(f"   获取到 {len(feed.entries)} 条")
        
        count = 0
        for entry in feed.entries[:10]:
            title = entry.title
            link = entry.link
            pub_date = entry.get('published', '')
            
            try:
                dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                ts = dt.isoformat()
            except:
                ts = datetime.now(timezone.utc).isoformat()
            
            source = f'Twitter-{account}'
            if insert_news(title, '', source, link, ts):
                count += 1
        
        print(f"   ✅ 插入 {count} 条")
        return count
    except Exception as e:
        print(f"   ❌ 错误：{e}")
        return 0

# 主任务
if __name__ == '__main__':
    total = 0
    
    # 1. Finnhub 新闻 (Reuters, CNBC, Bloomberg)
    total += fetch_finnhub_news()
    
    # 2. RSS 新闻
    total += fetch_rss_news('中国新闻网财经', 'https://www.chinanews.com.cn/rss/finance.xml')
    total += fetch_rss_news('Bloomberg', 'https://feeds.bloomberg.com/markets/news.rss')
    total += fetch_rss_news('Investing.com', 'https://cn.investing.com/rss/news.rss')
    total += fetch_rss_news('CNBC Top News', 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147')
    
    # 3. Twitter 新闻
    for account in ['Reuters', 'Bloomberg', 'WSJ', 'CNBC', 'FinancialTimes']:
        total += fetch_twitter_nitter(account)
    
    # 4. GitHub
    total += fetch_rss_news('GitHub', 'https://github.blog/feed/')
    
    print(f"\n{'='*50}")
    print(f"✅ 完成！共插入 {total} 条新闻")
    print(f"{'='*50}")
