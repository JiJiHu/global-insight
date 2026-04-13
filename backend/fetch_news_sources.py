#!/usr/bin/env python3
"""
多新闻源抓取脚本
- 中国新闻网财经 RSS
- Twitter/X 财经新闻
- 其他可访问的新闻源
"""
import sys
import feedparser
import requests
from datetime import datetime, timedelta
from db import get_db_connection
import time

# 新闻源配置
NEWS_SOURCES = {
    '中国新闻网财经': {
        'type': 'rss',
        'url': 'https://www.chinanews.com.cn/rss/finance.xml',
        'enabled': True
    },
    'Twitter财经': {
        'type': 'twitter',
        'accounts': [
            'Reuters',
            'Bloomberg',
            'CNBC',
            'WSJ',
            'FinancialTimes',
        ],
        'enabled': True
    },
    '央视网财经': {
        'type': 'web',
        'url': 'http://finance.cctv.com/',
        'enabled': False  # 需要提取逻辑
    },
    '经济参考报': {
        'type': 'web',
        'url': 'http://www.jjckb.cn/',
        'enabled': False
    },
    '第一财经': {
        'type': 'web',
        'url': 'https://www.yicai.com/',
        'enabled': False
    }
}

def simple_sentiment(text):
    """简单情感分析"""
    text_lower = text.lower()
    
    positive = [
        '涨', '上涨', '增长', '利好', '强劲', '突破', '新高',
        'rise', 'gain', 'grow', 'surge', 'jump', 'beat', 'record', 'strong', 'positive', 'up'
    ]
    negative = [
        '跌', '下跌', '跌幅', '负面', '下滑', '暴跌',
        'fall', 'drop', 'decline', 'crash', 'plunge', 'miss', 'weak', 'negative', 'down', 'loss'
    ]
    
    pos_count = sum(1 for word in positive if word in text_lower)
    neg_count = sum(1 for word in negative if word in text_lower)
    
    if pos_count > neg_count:
        return 0.6, '积极'
    elif neg_count > pos_count:
        return -0.6, '消极'
    else:
        return 0.0, '中性'

def fetch_rss(source_name, config):
    """抓取 RSS 源"""
    print(f"\n📰 抓取 RSS: {source_name}")
    print(f"   URL: {config['url']}")
    
    try:
        # 使用 requests 获取 RSS（避免 feedparser 直接请求的网络问题）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(config['url'], headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析 RSS
        feed = feedparser.parse(response.content)
        
        if not feed.entries:
            print(f"   ⚠️ 未获取到文章")
            return 0
        
        print(f"   ✅ 获取到 {len(feed.entries)} 篇文章")
        
        # 保存到数据库
        saved = 0
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            for entry in feed.entries[:20]:  # 最多保存 20 条
                title = entry.get('title', '')
                link = entry.get('link', '')
                published = entry.get('published', '')
                summary = entry.get('summary', '')
                
                if not title:
                    continue
                
                # 检查是否已存在
                cur.execute("SELECT id FROM news WHERE title = %s", (title,))
                if cur.fetchone():
                    continue
                
                # 如果 summary 为空，使用 title
                if not summary or len(summary.strip()) == 0:
                    summary = title
                
                # 情感分析
                score, label = simple_sentiment(title + " " + summary)
                
                # 解析时间
                try:
                    created_at = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')
                except:
                    created_at = datetime.now()
                
                # 插入数据库
                cur.execute("""
                    INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    title,
                    summary[:2000],  # 限制长度
                    source_name,
                    label,
                    score,
                    link,
                    created_at
                ))
                saved += 1
            
            conn.commit()
            cur.close()
        
        print(f"   ✅ 保存 {saved} 条")
        return saved
        
    except Exception as e:
        print(f"   ❌ 失败：{e}")
        return 0

def fetch_twitter_via_jina(accounts):
    """
    通过 Jina AI 读取 Twitter 账号
    Jina AI 可以绕过 Twitter 的反爬虫
    """
    print(f"\n🐦 抓取 Twitter财经新闻")
    print(f"   账号：{', '.join(accounts)}")
    
    total_saved = 0
    
    for account in accounts:
        try:
            # 使用 Jina AI 读取 Twitter
            twitter_url = f"https://x.com/{account}"
            jina_url = f"https://r.jina.ai/{twitter_url}"
            
            print(f"   📖 读取 @{account}...")
            
            response = requests.get(jina_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            if response.status_code != 200:
                print(f"      ⚠️ 失败：HTTP {response.status_code}")
                continue
            
            content = response.text
            
            # 解析 Jina 返回的内容
            lines = content.strip().split('\n')
            
            # 提取推文 - 更智能的解析
            tweets = []
            in_posts_section = False
            
            for line in lines:
                line = line.strip()
                
                # 检测是否进入推文区域
                if "## Reuters's posts" in line or "##" in line and "posts" in line.lower():
                    in_posts_section = True
                    continue
                
                # 跳过空行和元数据
                if not line or len(line) < 30:
                    continue
                
                # 跳过图片链接、URL 等
                if line.startswith('http') or line.startswith('![') or line.startswith('[!'):
                    continue
                
                # 跳过账号信息行
                if '@' in line and 'Follow' in line:
                    continue
                
                # 保留看起来像推文的内容
                if in_posts_section and len(line) > 30 and len(line) < 500:
                    tweets.append(line)
            
            # 如果没有检测到 posts 区域，尝试直接提取较长的文本行
            if not tweets:
                for line in lines:
                    line = line.strip()
                    if len(line) > 50 and len(line) < 400 and not line.startswith('http'):
                        tweets.append(line)
            
            if not tweets:
                print(f"      ⚠️ 未提取到推文")
                continue
            
            print(f"      提取到 {len(tweets)} 条推文")
            
            # 保存推文到新闻数据库
            saved = 0
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                for tweet in tweets[:10]:  # 每个账号最多 10 条
                    title = tweet[:200]  # 推文作为标题
                    content = tweet
                    
                    # 检查是否已存在
                    cur.execute("SELECT id FROM news WHERE title = %s", (title,))
                    if cur.fetchone():
                        continue
                    
                    # 情感分析
                    score, label = simple_sentiment(title + " " + content)
                    
                    # 插入数据库
                    cur.execute("""
                        INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        title,
                        content,
                        f'Twitter-{account}',
                        label,
                        score,
                        twitter_url,
                        datetime.now()
                    ))
                    saved += 1
                
                conn.commit()
                cur.close()
            
            print(f"      ✅ 保存 {saved} 条")
            total_saved += saved
            
            # 避免请求过快
            time.sleep(2)
            
        except Exception as e:
            print(f"      ❌ 失败：{e}")
            import traceback
            traceback.print_exc()
    
    return total_saved

def fetch_all_sources():
    """抓取所有启用的新闻源"""
    print(f"\n📰 开始抓取多源新闻 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    total = 0
    
    # 1. RSS 源
    for name, config in NEWS_SOURCES.items():
        if config.get('enabled') and config['type'] == 'rss':
            total += fetch_rss(name, config)
    
    # 2. Twitter 源
    twitter_config = NEWS_SOURCES.get('Twitter财经', {})
    if twitter_config.get('enabled'):
        total += fetch_twitter_via_jina(twitter_config.get('accounts', []))
    
    # 3. Web 源（暂不启用，需要提取逻辑）
    # for name, config in NEWS_SOURCES.items():
    #     if config.get('enabled') and config['type'] == 'web':
    #         print(f"\n⏭️  跳过 Web 源：{name} (需要提取逻辑)")
    
    print("\n" + "=" * 60)
    print(f"✅ 抓取完成！共 {total} 条")
    print("=" * 60)
    
    # 统计
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM news")
        total_news = cur.fetchone()[0]
        cur.execute("""
            SELECT source, COUNT(*) as count 
            FROM news 
            GROUP BY source 
            ORDER BY count DESC 
            LIMIT 15
        """)
        by_source = cur.fetchall()
        
        print(f"\n📊 新闻总数：{total_news}")
        print("\n按来源分布:")
        for source, count in by_source:
            bar = '█' * min(count // 10, 50)
            print(f"   {source:25} {count:5} {bar}")
        
        cur.close()
    
    return total

if __name__ == "__main__":
    fetch_all_sources()
