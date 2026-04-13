#!/usr/bin/env python3
"""
从 RSS 订阅源获取财经新闻
数据源：
- CNBC
- Reuters Business
- Bloomberg
- 华尔街见闻
"""

import feedparser
from datetime import datetime, timezone
from db import get_db_connection
import hashlib

# RSS 订阅源
RSS_FEEDS = [
    {
        'name': 'CNBC Top News',
        'url': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114',
        'category': 'us'
    },
    {
        'name': 'Reuters Business',
        'url': 'https://feeds.reuters.com/reuters/businessNews',
        'category': 'us'
    },
    {
        'name': 'Bloomberg Markets',
        'url': 'https://feeds.bloomberg.com/markets/news.rss',
        'category': 'us'
    },
    {
        'name': 'Investing.com',
        'url': 'https://cn.investing.com/rss/news.rss',
        'category': 'global'
    }
]

def calculate_sentiment(title, summary=''):
    """简单的情感分析（基于关键词）"""
    positive_words = ['rise', 'gain', 'grow', 'up', 'beat', 'surge', 'jump', 'rally', 'bull', 'positive', 'optimistic']
    negative_words = ['fall', 'drop', 'decline', 'down', 'miss', 'plunge', 'slump', 'bear', 'negative', 'pessimistic', 'war', 'conflict', 'crisis']
    
    text = (title + ' ' + summary).lower()
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in negative_words)
    
    if pos_count > neg_count:
        return 'positive', 0.7
    elif neg_count > pos_count:
        return 'negative', 0.7
    else:
        return 'neutral', 0.5

def dedup_news(news_list):
    """基于标题去重"""
    seen = set()
    unique_news = []
    
    for news in news_list:
        # 使用标题的 MD5 作为唯一标识
        title_hash = hashlib.md5(news['title'].encode()).hexdigest()
        if title_hash not in seen:
            seen.add(title_hash)
            unique_news.append(news)
    
    return unique_news

def fetch_rss_feeds():
    """获取所有 RSS 订阅源的新闻"""
    print("\n📰 开始获取 RSS 新闻...")
    
    all_news = []
    
    for feed_info in RSS_FEEDS:
        try:
            print(f"  获取 {feed_info['name']}...")
            feed = feedparser.parse(feed_info['url'])
            
            for entry in feed.entries[:10]:  # 每个源取最新 10 条
                title = entry.get('title', 'No title')
                summary = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')
                published = entry.get('published_parsed', datetime.now().timetuple())
                
                # 情感分析
                sentiment_label, sentiment_score = calculate_sentiment(title, summary)
                
                # 确保 summary 不为空
                if not summary or len(summary.strip()) == 0:
                    summary = title  # 至少使用标题作为内容
                
                news_item = {
                    'title': title,
                    'summary': summary[:500] if summary else title,  # 限制长度
                    'source': feed_info['name'],
                    'url': link,
                    'sentiment_label': sentiment_label,
                    'sentiment_score': sentiment_score,
                    'published_at': datetime(*published[:6], tzinfo=timezone.utc) if len(published) >= 6 else datetime.now(timezone.utc),
                    'category': feed_info['category']
                }
                
                all_news.append(news_item)
            
            print(f"    ✅ 获取 {len(feed.entries)} 条")
            
        except Exception as e:
            print(f"    ❌ {feed_info['name']} 失败：{e}")
    
    # 去重
    unique_news = dedup_news(all_news)
    print(f"\n✅ 去重后：{len(unique_news)} 条新闻")
    
    return unique_news

def save_to_database(news_list):
    """保存新闻到数据库"""
    if not news_list:
        return 0
    
    count = 0
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        for news in news_list:
            try:
                # 检查是否已存在（基于 URL）
                cur.execute("SELECT id FROM news WHERE url = %s", (news['url'],))
                if cur.fetchone():
                    continue  # 跳过已存在的新闻
                
                cur.execute("""
                    INSERT INTO news 
                    (title, content, source, url, sentiment_score, sentiment_label, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    news['title'],
                    news['summary'],
                    news['source'],
                    news['url'],
                    news['sentiment_score'],
                    news['sentiment_label'],
                    news['published_at']
                ))
                count += 1
                
            except Exception as e:
                print(f"⚠️ 保存失败：{e}")
        
        conn.commit()
        cur.close()
    
    print(f"💾 已保存 {count} 条新新闻到数据库")
    return count

def fetch_all():
    """主函数"""
    news_list = fetch_rss_feeds()
    saved_count = save_to_database(news_list)
    return saved_count

if __name__ == "__main__":
    fetch_all()
