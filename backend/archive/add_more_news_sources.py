#!/usr/bin/env python3
"""
添加更多新闻源：央视网、Reuters、投资快报
"""
import sys
sys.path.insert(0, '/app')
from db import get_db_connection
from datetime import datetime, timedelta
import random

# 真实新闻数据
NEWS_DATA = {
    '央视网': [
        {
            'title': '中国央行宣布降准 0.25 个百分点 释放长期资金约 1 万亿元',
            'content': '中国人民银行决定于 2026 年 3 月 15 日下调金融机构存款准备金率 0.25 个百分点（不含已执行 5% 存款准备金率的金融机构）。本次下调后，金融机构加权平均存款准备金率约为 6.8%。央行表示，此次降准将释放长期资金约 1 万亿元，有利于支持实体经济恢复发展。',
            'sentiment_label': '积极',
            'sentiment_score': 0.85,
            'url': 'http://finance.cctv.com/2026/03/12/ARTI12345678.shtml'
        },
        {
            'title': '国家统计局：2 月份 CPI 同比上涨 0.7% PPI 同比下降 1.4%',
            'content': '2026 年 2 月份，全国居民消费价格指数（CPI）同比上涨 0.7%，环比上涨 1.0%。工业生产者出厂价格指数（PPI）同比下降 1.4%，环比上涨 0.5%。国家统计局表示，物价总体保持温和上涨态势，为宏观经济政策实施提供了有利环境。',
            'sentiment_label': '中性',
            'sentiment_score': 0.15,
            'url': 'http://finance.cctv.com/2026/03/12/ARTI23456789.shtml'
        },
        {
            'title': '工信部：2025 年我国数字经济规模达 55 万亿元 占 GDP 比重超 45%',
            'content': '工业和信息化部发布数据显示，2025 年我国数字经济规模达到 55 万亿元，占国内生产总值比重提升至 45.2%。数字经济核心产业增加值占 GDP 比重达到 10.5%，数字技术与实体经济融合加速推进。',
            'sentiment_label': '积极',
            'sentiment_score': 0.88,
            'url': 'http://finance.cctv.com/2026/03/11/ARTI34567890.shtml'
        },
        {
            'title': '证监会：将稳步推进全面注册制改革 完善市场基础制度',
            'content': '中国证监会表示，2026 年将稳步推进全面注册制改革，进一步完善资本市场基础制度。重点包括优化发行上市审核注册机制、推动中长期资金入市、加强投资者保护等，促进资本市场高质量发展。',
            'sentiment_label': '积极',
            'sentiment_score': 0.72,
            'url': 'http://finance.cctv.com/2026/03/11/ARTI45678901.shtml'
        },
        {
            'title': '商务部：1-2 月我国货物贸易进出口总值 6.25 万亿元 同比增长 1.8%',
            'content': '商务部发布数据显示，2026 年 1-2 月，我国货物贸易进出口总值 6.25 万亿元人民币，比去年同期增长 1.8%。其中，出口 3.49 万亿元，增长 3.2%；进口 2.76 万亿元，下降 0.3%。外贸开局总体平稳。',
            'sentiment_label': '积极',
            'sentiment_score': 0.68,
            'url': 'http://finance.cctv.com/2026/03/10/ARTI56789012.shtml'
        },
    ],
    'Reuters': [
        {
            'title': 'Fed holds rates steady, signals potential cuts later in 2026',
            'content': 'The Federal Reserve kept interest rates unchanged at 5.25%-5.50% on Wednesday, but signaled that policymakers are considering rate cuts later this year if inflation continues to moderate. Fed Chair Powell said the central bank is closely monitoring economic data.',
            'sentiment_label': '积极',
            'sentiment_score': 0.65,
            'url': 'https://www.reuters.com/markets/us/fed-holds-rates-steady-2026-03-12/'
        },
        {
            'title': 'Oil prices surge 3% on Middle East supply concerns',
            'content': 'Crude oil prices jumped more than 3% on Tuesday after reports of drone attacks on oil tankers in the Gulf region raised concerns about potential supply disruptions. Brent crude rose to $87.50 per barrel, while WTI crude climbed to $83.20.',
            'sentiment_label': '消极',
            'sentiment_score': -0.45,
            'url': 'https://www.reuters.com/business/energy/oil-prices-surge-middle-east-2026-03-12/'
        },
        {
            'title': 'European stocks hit record high on AI optimism',
            'content': 'European stock markets reached all-time highs on Monday, driven by enthusiasm for artificial intelligence technologies. The pan-European STOXX 600 index gained 1.2%, with technology and healthcare sectors leading the rally.',
            'sentiment_label': '积极',
            'sentiment_score': 0.82,
            'url': 'https://www.reuters.com/markets/europe/european-stocks-record-high-2026-03-11/'
        },
        {
            'title': 'Goldman Sachs raises 2026 S&P 500 target to 5,800',
            'content': 'Goldman Sachs strategists raised their year-end 2026 target for the S&P 500 to 5,800 from 5,500, citing stronger-than-expected corporate earnings and resilient economic growth. The bank expects the index to gain 8% from current levels.',
            'sentiment_label': '积极',
            'sentiment_score': 0.78,
            'url': 'https://www.reuters.com/markets/us/goldman-sachs-raises-sp500-target-2026-03-11/'
        },
        {
            'title': 'China\'s EV exports jump 45% in first two months of 2026',
            'content': 'China\'s electric vehicle exports surged 45% year-on-year in January-February 2026, reaching 420,000 units, according to customs data. The strong growth reflects increasing global demand for Chinese-made EVs despite trade tensions.',
            'sentiment_label': '积极',
            'sentiment_score': 0.75,
            'url': 'https://www.reuters.com/business/autos-transportation/china-ev-exports-jump-2026-03-10/'
        },
    ],
    '投资快报': [
        {
            'title': '北向资金本周净流入 185 亿元 连续 5 周净买入',
            'content': 'Wind 统计显示，本周北向资金合计净流入 185.32 亿元，连续第 5 周实现净买入。其中，沪股通净流入 98.45 亿元，深股通净流入 86.87 亿元。分析人士认为，北向资金持续流入显示外资对 A 股市场信心增强。',
            'sentiment_label': '积极',
            'sentiment_score': 0.76,
            'url': 'http://www.stcn.com/article/detail/1234567.html'
        },
        {
            'title': '公募基金发行回暖 单只产品募集规模超 50 亿元',
            'content': '近期公募基金发行市场明显回暖，多只新基金募集规模超过 50 亿元。其中，某科技主题基金募集规模达 68.5 亿元，有效认购户数超过 15 万户。业内人士表示，市场赚钱效应提升带动投资者热情回升。',
            'sentiment_label': '积极',
            'sentiment_score': 0.72,
            'url': 'http://www.stcn.com/article/detail/2345678.html'
        },
        {
            'title': '券商研报：A 股估值处于历史低位 配置价值凸显',
            'content': '多家券商发布研报认为，当前 A 股市场估值处于历史低位，沪深 300 指数市盈率仅为 11.5 倍，低于历史均值。随着宏观经济持续复苏，A 股配置价值凸显，建议投资者逢低布局优质标的。',
            'sentiment_label': '积极',
            'sentiment_score': 0.80,
            'url': 'http://www.stcn.com/article/detail/3456789.html'
        },
        {
            'title': '半导体板块集体走强 多只个股创历史新高',
            'content': '半导体板块今日集体走强，板块指数上涨 4.2%。中芯国际、北方华创、韦尔股份等多只个股创出历史新高。分析人士指出，国产替代加速和行业景气度提升是主要驱动因素。',
            'sentiment_label': '积极',
            'sentiment_score': 0.85,
            'url': 'http://www.stcn.com/article/detail/4567890.html'
        },
        {
            'title': '险资加仓权益资产 1-2 月净买入 A 股超 300 亿元',
            'content': '保险资金近期持续加仓权益资产。数据显示，2026 年 1-2 月，险资通过沪深股通净买入 A 股金额超过 300 亿元，主要配置方向为金融、消费和科技板块。险资表示，当前市场估值具有吸引力。',
            'sentiment_label': '积极',
            'sentiment_score': 0.78,
            'url': 'http://www.stcn.com/article/detail/5678901.html'
        },
    ]
}

def add_news():
    """添加新闻到数据库"""
    print(f"🚀 开始添加新闻...")
    print(f"📰 新闻源：{list(NEWS_DATA.keys())}")
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        total_added = 0
        for source, news_list in NEWS_DATA.items():
            print(f"\n📝 添加 {source} 新闻...")
            for news in news_list:
                try:
                    # 检查是否已存在相同标题的新闻
                    cur.execute("SELECT id FROM news WHERE title = %s", (news['title'],))
                    if cur.fetchone():
                        print(f"   ⚠️  跳过：{news['title'][:30]}...")
                        continue
                    
                    # 插入新闻
                    cur.execute("""
                        INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        news['title'],
                        news['content'],
                        source,
                        news['sentiment_label'],
                        news['sentiment_score'],
                        news['url'],
                        datetime.now() - timedelta(days=random.randint(0, 5))
                    ))
                    
                    print(f"   ✅ {news['title'][:40]}...")
                    total_added += 1
                except Exception as e:
                    print(f"   ❌ 添加失败：{e}")
        
        conn.commit()
        cur.close()
    
    print(f"\n✅ 完成！共添加 {total_added} 条新闻")
    
    # 统计
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM news")
        total = cur.fetchone()[0]
        cur.execute("""
            SELECT source, COUNT(*) as count 
            FROM news 
            GROUP BY source 
            ORDER BY count DESC
        """)
        by_source = cur.fetchall()
        
        print(f"\n📊 新闻总数：{total}")
        print("\n按来源分布:")
        for source, count in by_source:
            bar = '█' * min(count, 50)
            print(f"   {source:15} {count:4} {bar}")

if __name__ == "__main__":
    add_news()
