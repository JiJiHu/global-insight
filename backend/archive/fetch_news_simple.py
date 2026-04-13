#!/usr/bin/env python3
"""
简化版新闻抓取脚本 - 不做向量化
- 从 Finnhub 获取新闻
- 直接存入数据库（不生成 embedding）
"""
import requests
import time
from datetime import datetime, timedelta
from db import insert_news

def fetch_finnhub_news(category='general', limit=50):
    """
    从 Finnhub 获取新闻
    category: general, forex, crypto, merger
    """
    API_KEY = "d6l40k1r01qm1k1qg4jgd6l40k1r01qm1k1qg4jg"  # 从配置中获取

    params = {
        'token': API_KEY,
        'category': category,
        'from': int((datetime.now() - timedelta(days=30)).timestamp()),  # 只取最近30天
        'to': int(datetime.now().timestamp())
    }

    try:
        response = requests.get('https://finnhub.io/api/v1/news', params=params, timeout=10)
        data = response.json()

        if not isinstance(data, list):
            print(f"⚠️ 返回数据格式错误: {type(data)}")
            return 0

        print(f"✅ 获取到 {len(data)} 条 {category} 新闻")

        # 存入数据库
        for item in data:
            title = item.get('headline', '')
            summary = item.get('summary', '')
            url = item.get('url', '')
            source = f"finnhub-{category}"

            # 简单的情感分析（基于关键词）
            sentiment_score, sentiment_label = simple_sentiment_analysis(title + " " + summary)

            insert_news(
                title=title,
                content=summary,
                source=source,
                url=url,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                embedding=None,  # 不生成向量
                related_symbols=[]
            )

        return len(data)

    except Exception as e:
        print(f"❌ 获取 {category} 新闻失败：{e}")
        return 0

def simple_sentiment_analysis(text):
    """
    简化版情感分析 - 基于关键词，不需要ML模型
    """
    positive_keywords = [
        '涨', '涨势', '上涨', '增长', '利好', '强劲',
        'breakthrough', 'surge', 'rally', 'gain', 'boost', 'positive'
    ]
    negative_keywords = [
        '跌', '下跌', '跌幅', '下跌', '负面', '跌势',
        'drop', 'fall', 'decline', 'loss', 'negative', 'crash'
    ]

    text_lower = text.lower()
    positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
    negative_count = sum(1 for kw in negative_keywords if kw in text_lower)

    if positive_count > negative_count:
        return 0.6, 'positive'
    elif negative_count > positive_count:
        return -0.6, 'negative'
    else:
        return 0.0, 'neutral'

def fetch_all_categories():
    """
    抓取所有分类的新闻
    """
    print(f"\n📰 开始抓取新闻 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    total = 0

    # 1. 一般财经新闻
    total += fetch_finnhub_news(category='general', limit=100)

    # 2. 外汇新闻
    total += fetch_finnhub_news(category='forex', limit=50)

    # 3. 加密货币新闻
    total += fetch_finnhub_news(category='crypto', limit=50)

    # 4. 并购新闻
    total += fetch_finnhub_news(category='merger', limit=50)

    print("\n" + "=" * 60)
    print(f"✅ 新闻抓取完成！共 {total} 条")
    print("=" * 60)

    return total

if __name__ == "__main__":
    # 循环抓取多次以增加数据量
    for i in range(5):  # 抓取5次
        print(f"\n第 {i+1}/5 轮抓取...")
        fetch_all_categories()
        time.sleep(10)  # 避免API限流

    # 统计
    from db import get_db_connection
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM news")
        result = cur.fetchone()
        print(f"\n📊 新闻总数：{result[0]} 条")
        print(f"   从 {result[1]}")
        print(f"   到 {result[2]}")
