#!/usr/bin/env python3
"""
实时新闻抓取脚本 - 替换静态测试数据
数据源：
- Reuters (http://feeds.reuters.com/Reuters/worldNews)
- 中国新闻网财经 (https://www.chinanews.com.cn/rss/finance.xml)
- 新浪财经 RSS
- RSSHub 生成的源
"""
import sys
sys.path.insert(0, '/app')
from db import get_db_connection
import feedparser
import requests
from datetime import datetime, timezone
import hashlib

# 真实 RSS 数据源配置
RSS_FEEDS = [
    # 国际财经
    {
        'name': 'CNBC - Top News',
        'url': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114',
        'category': 'global'
    },
    {
        'name': 'CNBC - Finance',
        'url': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000115',
        'category': 'global'
    },
    {
        'name': 'Bloomberg Markets',
        'url': 'https://feeds.bloomberg.com/markets/news.rss',
        'category': 'global'
    },
    {
        'name': 'Reuters - Google News',
        'url': 'https://news.google.com/rss/search?q=Reuters+finance+business&hl=en-US&gl=US&ceid=US:en',
        'category': 'global'
    },
    # 中国财经
    {
        'name': '中国新闻网财经',
        'url': 'https://www.chinanews.com.cn/rss/finance.xml',
        'category': 'china'
    },
    {
        'name': '中国日报财经',
        'url': 'https://www.chinadaily.com.cn/rss/business.xml',
        'category': 'china'
    },
    {
        'name': '新华社财经',
        'url': 'http://www.xinhuanet.com/fortune/fortune.xml',
        'category': 'china'
    },
]

def simple_sentiment(text):
    """简单情感分析"""
    text_lower = text.lower()
    
    # 英文正面词
    positive_en = ['rise', 'gain', 'grow', 'surge', 'jump', 'beat', 'record', 'strong', 'positive', 'up', 'rally', 'bull', 'optimistic']
    negative_en = ['fall', 'drop', 'decline', 'crash', 'plunge', 'miss', 'weak', 'negative', 'down', 'loss', 'slump', 'bear', 'pessimistic', 'war', 'conflict', 'crisis']
    
    # 中文正面词
    positive_cn = ['上涨', '增长', '突破', '利好', '强势', '创新高', '回暖', '复苏', '乐观']
    negative_cn = ['下跌', '下滑', '暴跌', '利空', '疲软', '亏损', '危机', '冲突', '战争', '悲观']
    
    score = 0
    for word in positive_en + positive_cn:
        if word in text_lower or word in text:
            score += 1
    for word in negative_en + negative_cn:
        if word in text_lower or word in text:
            score -= 1
    
    if score > 0:
        return 'positive', 0.7
    elif score < 0:
        return 'negative', -0.7
    else:
        return 'neutral', 0.0

def calculate_url_hash(url):
    """计算 URL 的 MD5 哈希用于去重"""
    return hashlib.md5(url.encode()).hexdigest()

def fetch_rss_feed(feed_info, limit=20):
    """从 RSS 源获取新闻"""
    print(f"  获取 {feed_info['name']}...")
    news_list = []
    
    try:
        # feedparser 不支持 timeout 参数，使用 requests 先获取
        response = requests.get(feed_info['url'], timeout=10)
        feed = feedparser.parse(response.content)
        
        if not feed.entries:
            print(f"    ⚠️ 无内容")
            return []
        
        for entry in feed.entries[:limit]:
            title = getattr(entry, 'title', '')
            if not title:
                continue
            
            # 获取链接
            url = getattr(entry, 'link', '')
            if not url:
                continue
            
            # 获取发布时间
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except:
                    published_at = datetime.now(timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                try:
                    published_at = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                except:
                    published_at = datetime.now(timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)
            
            # 获取摘要/内容
            content = ''
            if hasattr(entry, 'summary'):
                content = entry.summary[:1000]
            elif hasattr(entry, 'description'):
                content = entry.description[:1000]
            elif hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value[:1000] if entry.content else ''
            
            # 确保 content 不为空，至少使用标题
            if not content or len(content.strip()) == 0:
                content = title
            
            # 情感分析
            sentiment_label, sentiment_score = simple_sentiment(title + ' ' + content)
            
            news_item = {
                'title': title,
                'url': url,
                'source': feed_info['name'],
                'content': content,
                'sentiment_label': sentiment_label,
                'sentiment_score': sentiment_score,
                'published_at': published_at,
                'url_hash': calculate_url_hash(url)
            }
            news_list.append(news_item)
        
        print(f"    ✅ 获取 {len(news_list)} 条")
        
    except Exception as e:
        print(f"    ❌ {feed_info['name']} 失败：{e}")
    
    return news_list

def save_to_database(news_list):
    """保存新闻到数据库（带去重）"""
    if not news_list:
        return 0
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        saved = 0
        skipped = 0
        
        for news in news_list:
            try:
                # 检查是否已存在（通过 URL 哈希）
                cur.execute("SELECT id FROM news WHERE url_hash = %s", (news['url_hash'],))
                if cur.fetchone():
                    skipped += 1
                    continue
                
                # 插入新闻
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

def fetch_all_news():
    """获取所有 RSS 源新闻"""
    print("\n📰 开始获取实时新闻 - " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    all_news = []
    
    for feed_info in RSS_FEEDS:
        news_list = fetch_rss_feed(feed_info)
        all_news.extend(news_list)
    
    print(f"\n✅ 共获取 {len(all_news)} 条新闻")
    
    # 保存到数据库
    saved = save_to_database(all_news)
    
    # 统计
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM news")
        total = cur.fetchone()[0]
        cur.execute("SELECT MAX(created_at) FROM news")
        latest = cur.fetchone()[0]
        cur.close()
    
    print(f"📊 新闻总数：{total}")
    print(f"🕒 最新新闻：{latest}")
    print("=" * 60)
    
    return saved

if __name__ == "__main__":
    fetch_all_news()
