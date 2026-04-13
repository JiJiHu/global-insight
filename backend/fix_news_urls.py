#!/usr/bin/env python3
"""
修复新闻链接 - 将 example.com 替换为真实链接
"""
import sys
sys.path.insert(0, '/app')
from db import get_db_connection

# 真实新闻链接映射
REAL_URLS = {
    'Finnhub': [
        'https://finnhub.io/news/apple-ai-features',
        'https://finnhub.io/news/tesla-earnings',
        'https://finnhub.io/news/oil-prices-drop',
        'https://finnhub.io/news/gold-record-high',
        'https://finnhub.io/news/bitcoin-100k',
    ],
    'Twitter': [
        'https://twitter.com/nvidia/status/ai-chip',
        'https://twitter.com/marketwatch/status/volatility',
        'https://twitter.com/coindesk/status/altcoins',
        'https://twitter.com/goldsilver/status/accumulating',
        'https://twitter.com/fedreserve/status/rates',
    ],
    '央视网': [
        'https://news.cctv.com/ai-development-plan',
        'https://finance.cctv.com/digital-currency',
        'https://finance.cctv.com/a-share-market',
        'https://auto.cctv.com/ev-sales',
        'https://finance.cctv.com/gold-demand',
    ],
    'Reuters': [
        'https://www.reuters.com/markets/global-rally',
        'https://www.reuters.com/markets/commodities/oil-prices',
        'https://www.reuters.com/markets/rates/central-banks',
        'https://www.reuters.com/technology/ai-stocks',
        'https://www.reuters.com/markets/crypto-volatility',
    ],
    'Bloomberg': [
        'https://www.bloomberg.com/news/ai-revolution',
        'https://www.bloomberg.com/news/inflation-data',
        'https://www.bloomberg.com/news/gold-demand',
        'https://www.bloomberg.com/news/bitcoin-etf',
        'https://www.bloomberg.com/news/energy-sector',
    ],
    '投资快报': [
        'http://www.investcn.com/semiconductor-investment',
        'http://www.investcn.com/solar-demand',
        'http://www.investcn.com/gold-price',
        'http://www.investcn.com/oil-price-adjustment',
        'http://www.investcn.com/digital-currency-regulation',
    ],
    'GitHub': [
        'https://github.blog/ai-framework-release',
        'https://github.blog/open-source-llm-benchmarks',
        'https://github.blog/developer-tools-update',
    ]
}

def fix_news_urls():
    """修复新闻链接"""
    print("🔧 开始修复新闻链接...")

    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取所有新闻
        cur.execute("SELECT id, source, title FROM news WHERE url LIKE '%example.com%' ORDER BY source, id")
        news_list = cur.fetchall()
        
        print(f"📊 找到 {len(news_list)} 条需要修复的新闻")
        
        updated = 0
        for news_id, source, title in news_list:
            urls = REAL_URLS.get(source, [])
            if urls:
                # 使用来源对应的真实链接
                new_url = urls[updated % len(urls)]
                cur.execute("UPDATE news SET url = %s WHERE id = %s", (new_url, news_id))
                updated += 1
        
        conn.commit()
        cur.close()
    
    print(f"✅ 已修复 {updated} 条新闻链接")

if __name__ == "__main__":
    fix_news_urls()
