#!/usr/bin/env python3
"""
从 Twitter/X 抓取财经新闻
使用 x-reader 技能或备用方案
"""
import sys
sys.path.insert(0, '/app')
from db import get_db_connection
import subprocess
import json
from datetime import datetime, timezone
import hashlib

# 财经相关的 Twitter 账号
TWITTER_ACCOUNTS = [
    {'handle': 'business', 'name': 'Bloomberg Business'},
    {'handle': 'CNBC', 'name': 'CNBC'},
    {'handle': 'Reuters', 'name': 'Reuters'},
    {'handle': 'WSJ', 'name': 'Wall Street Journal'},
    {'handle': 'FinancialTimes', 'name': 'Financial Times'},
]

def simple_sentiment(text):
    """简单情感分析"""
    text_lower = text.lower()
    
    positive = ['rise', 'gain', 'grow', 'surge', 'jump', 'beat', 'record', 'strong', 'positive', 'up', 'rally', 'bull']
    negative = ['fall', 'drop', 'decline', 'crash', 'plunge', 'miss', 'weak', 'negative', 'down', 'loss', 'slump', 'bear']
    
    score = sum(1 for word in positive if word in text_lower) - sum(1 for word in negative if word in text_lower)
    
    if score > 0:
        return 'positive', 0.7
    elif score < 0:
        return 'negative', -0.7
    else:
        return 'neutral', 0.0

def calculate_url_hash(url):
    """计算 URL 的 MD5 哈希"""
    return hashlib.md5(url.encode()).hexdigest()

def fetch_twitter_account(account):
    """抓取单个 Twitter 账号的新闻（备用方案：使用 Nitter RSS）"""
    print(f"  获取 @{account['handle']}...")
    news_list = []
    
    try:
        # 使用 Nitter RSS（Twitter 的 RSS 镜像）
        import feedparser
        import requests
        
        nitter_instances = [
            'https://nitter.net',
            'https://nitter.privacy.com.de',
            'https://nitter.snopyta.org',
        ]
        
        for instance in nitter_instances:
            try:
                rss_url = f"{instance}/{account['handle']}/rss"
                response = requests.get(rss_url, timeout=10)
                
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    
                    for entry in feed.entries[:10]:
                        title = getattr(entry, 'title', '')
                        if not title or len(title) < 10:
                            continue
                        
                        link = getattr(entry, 'link', '')
                        published = getattr(entry, 'published_parsed', None)
                        
                        if published:
                            published_at = datetime(*published[:6], tzinfo=timezone.utc)
                        else:
                            published_at = datetime.now(timezone.utc)
                        
                        # 情感分析
                        sentiment_label, sentiment_score = simple_sentiment(title)
                        
                        news_item = {
                            'title': title[:200],
                            'content': title,
                            'url': link,
                            'source': account['name'],
                            'sentiment_label': sentiment_label,
                            'sentiment_score': sentiment_score,
                            'url_hash': calculate_url_hash(link),
                            'published_at': published_at
                        }
                        
                        news_list.append(news_item)
                    
                    if news_list:
                        print(f"    ✅ 获取 {len(news_list)} 条 (via {instance})")
                        break
                        
            except Exception:
                continue
        
        if not news_list:
            print(f"    ⚠️ 无法获取")
            
    except Exception as e:
        print(f"    ❌ 错误：{e}")
    
    return news_list

def save_to_database(news_list):
    """保存新闻到数据库"""
    if not news_list:
        return 0
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        saved = 0
        skipped = 0
        
        for news in news_list:
            try:
                # 检查是否已存在
                cur.execute("SELECT id FROM news WHERE url_hash = %s", (news['url_hash'],))
                if cur.fetchone():
                    skipped += 1
                    continue
                
                cur.execute("""
                    INSERT INTO news (
                        title, content, source, sentiment_label,
                        sentiment_score, url, url_hash, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    news['title'],
                    news['content'][:2000],
                    news['source'],
                    news['sentiment_label'],
                    news['sentiment_score'],
                    news['url'],
                    news['url_hash'],
                    news['published_at']
                ))
                saved += 1
                
            except Exception as e:
                print(f"⚠️ 保存失败：{e}")
                skipped += 1
        
        conn.commit()
        cur.close()
    
    print(f"💾 新增 {saved} 条，跳过 {skipped} 条重复")
    return saved

def fetch_all():
    """获取所有 Twitter 新闻"""
    print("\n🐦 开始获取 Twitter 新闻 - " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    all_news = []
    
    for account in TWITTER_ACCOUNTS[:3]:  # 限制 3 个账号
        news_list = fetch_twitter_account(account)
        all_news.extend(news_list)
    
    print(f"\n✅ 共获取 {len(all_news)} 条新闻")
    
    if all_news:
        saved = save_to_database(all_news)
    else:
        saved = 0
        print("⚠️ 无新闻可保存")
    
    return saved

if __name__ == "__main__":
    fetch_all()
