#!/usr/bin/env python3
"""
添加新闻来源信息（为分标签页做准备）
"""
import sys
sys.path.insert(0, '/app')
from db import get_db_connection
import random

# 定义新闻来源和它们的新闻
NEWS_SOURCES = {
    'Finnhub': [
        {'title': 'Apple Announces New AI Features for iPhone', 'sentiment_label': '积极', 'sentiment_score': 0.85},
        {'title': 'Tesla Stock Surges After Strong Earnings Report', 'sentiment_label': '积极', 'sentiment_score': 0.80},
        {'title': 'Oil Prices Drop amid Global Economic Concerns', 'sentiment_label': '消极', 'sentiment_score': -0.60},
        {'title': 'Gold Reaches Record High Amid Market Uncertainty', 'sentiment_label': '积极', 'sentiment_score': 0.75},
        {'title': 'Bitcoin Breaks $100,000 Milestone', 'sentiment_label': '积极', 'sentiment_score': 0.90},
    ],
    'Twitter': [
        {'title': 'BREAKING: NVIDIA announces new AI chip architecture', 'sentiment_label': '积极', 'sentiment_score': 0.88},
        {'title': '⚠️ Market volatility expected next week', 'sentiment_label': '中性', 'sentiment_score': 0.10},
        {'title': '🚀 Altcoins rallying behind Bitcoin surge', 'sentiment_label': '积极', 'sentiment_score': 0.70},
        {'title': '💸 Institutional investors accumulating gold', 'sentiment_label': '积极', 'sentiment_score': 0.65},
        {'title': '⏳ Fed decision pending rates unchanged', 'sentiment_label': '中性', 'sentiment_score': 0.05},
    ],
    '央视网': [
        {'title': '我国发布新一代人工智能发展规划', 'sentiment_label': '积极', 'sentiment_score': 0.92},
        {'title': '央行数字货币试点范围扩大', 'sentiment_label': '积极', 'sentiment_score': 0.85},
        {'title': 'A股市场保持稳定运行态势', 'sentiment_label': '中性', 'sentiment_score': 0.10},
        {'title': '新能源汽车销量再创新高', 'sentiment_label': '积极', 'sentiment_score': 0.88},
        {'title': '黄金投资需求持续增长', 'sentiment_label': '积极', 'sentiment_score': 0.75},
    ],
    'Reuters': [
        {'title': 'Global Markets Rally on Positive Economic Data', 'sentiment_label': '积极', 'sentiment_score': 0.78},
        {'title': 'Oil Prices Hit 3-Month High', 'sentiment_label': '积极', 'sentiment_score': 0.72},
        {'title': 'Central Banks Hold Rates Steady', 'sentiment_label': '中性', 'sentiment_score': 0.05},
        {'title': 'Tech Stocks Lead Gains as AI Excitement Builds', 'sentiment_label': '积极', 'sentiment_score': 0.85},
        {'title': 'Crypto Markets See Increased Volatility', 'sentiment_label': '中性', 'sentiment_score': -0.15},
    ],
    'Bloomberg': [
        {'title': 'AI Revolution: How Tech Giants Are Racing', 'sentiment_label': '积极', 'sentiment_score': 0.90},
        {'title': 'Markets Brace for Key Inflation Data', 'sentiment_label': '中性', 'sentiment_score': -0.05},
        {'title': 'Gold Demand Surges from Central Banks', 'sentiment_label': '积极', 'sentiment_score': 0.82},
        {'title': 'Bitcoin ETFs Attract Record Inflows', 'sentiment_label': '积极', 'sentiment_score': 0.88},
        {'title': 'Energy Sector Faces Supply Chain Challenges', 'sentiment_label': '消极', 'sentiment_score': -0.65},
    ],
    '投资快报': [
        {'title': '半导体行业迎来新一轮投资热潮', 'sentiment_label': '积极', 'sentiment_score': 0.82},
        {'title': '光伏产业链需求旺盛', 'sentiment_label': '积极', 'sentiment_score': 0.78},
        {'title': '国内黄金现货价格逼近历史高点', 'sentiment_label': '积极', 'sentiment_score': 0.75},
        {'title': '成品油价格上调预期增强', 'sentiment_label': '积极', 'sentiment_score': 0.68},
        {'title': '数字货币监管政策征求意见稿发布', 'sentiment_label': '中性', 'sentiment_score': 0.12},
    ]
}

def add_news_with_sources():
    """添加带有来源的新闻"""
    print(f"🚀 开始添加新闻（按来源分类）...")

    with get_db_connection() as conn:
        cur = conn.cursor()

        for source, news_items in NEWS_SOURCES.items():
            print(f"\n📰 来源: {source}")
            for item in news_items:
                content = f"这是关于 {item['title']} 的详细内容。该新闻反映了当前市场的重要动态，投资者应密切关注。"
                url = f"https://example.com/news/{source.lower()}/{random.randint(1000, 9999)}"

                cur.execute("""
                    INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    item['title'],
                    content,
                    source,
                    item['sentiment_label'],
                    item['sentiment_score'],
                    url
                ))
                print(f"   ✅ {item['title'][:40]}...")

        conn.commit()
        cur.close()

    print("\n✅ 新闻添加完成!")

    # 统计
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM news")
        total = cur.fetchone()[0]
        cur.execute("SELECT source, COUNT(*) FROM news GROUP BY source ORDER BY count DESC")
        by_source = cur.fetchall()
        print(f"\n📊 新闻总数: {total}")
        print("\n按来源分布:")
        for source, count in by_source:
            print(f"   - {source}: {count} 条")

if __name__ == "__main__":
    add_news_with_sources()
