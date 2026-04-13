#!/usr/bin/env python3
"""
财经新闻抓取脚本
- Finnhub News API (免费)
- 向量化后存入数据库
"""
import sys
import requests
from datetime import datetime, timedelta
sys.path.insert(0, '/root/finance-dashboard/backend')

from vectorize_news import NewsVectorizer
from config import FINNHUB_API_KEY, WATCHLIST
from db import insert_news

def fetch_finnhub_news(symbols=None, from_date=None, to_date=None):
    """从 Finnhub 获取新闻"""
    news_list = []
    
    # 获取一般财经新闻
    try:
        # 获取最近 24 小时的新闻
        params = {
            'token': FINNHUB_API_KEY,
            'category': 'general',
            'from': int((datetime.now() - timedelta(hours=24)).timestamp()),
            'to': int(datetime.now().timestamp())
        }
        
        response = requests.get('https://finnhub.io/api/v1/news', params=params, timeout=10)
        data = response.json()
        
        if data and isinstance(data, list):
            for item in data[:20]:  # 限制 20 条
                news = {
                    'title': item.get('headline', ''),
                    'content': item.get('summary', ''),
                    'source': 'finnhub',
                    'url': item.get('url', '')
                }
                news_list.append(news)
            
            print(f"✅ 获取到 {len(news_list)} 条财经新闻")
    except Exception as e:
        print(f"❌ 获取新闻失败：{e}")
    
    # 获取特定公司的新闻
    if symbols:
        for symbol in symbols[:5]:  # 限制 5 个公司避免超限
            try:
                params = {
                    'token': FINNHUB_API_KEY,
                    'symbol': symbol
                }
                
                response = requests.get('https://finnhub.io/api/v1/company-news', params=params, timeout=10)
                data = response.json()
                
                if data and isinstance(data, list):
                    for item in data[:5]:  # 每个公司 5 条
                        news = {
                            'title': item.get('headline', ''),
                            'content': item.get('summary', ''),
                            'source': f'finnhub-{symbol}',
                            'url': item.get('url', '')
                        }
                        news_list.append(news)
                    
                    print(f"✅ {symbol}: {len([n for n in data[:5]])} 条新闻")
            except Exception as e:
                print(f"❌ {symbol} 新闻失败：{e}")
    
    return news_list

def process_news(news_list):
    """处理新闻并向量化"""
    if not news_list:
        print("⚠️ 没有新闻需要处理")
        return
    
    print(f"\n🧠 开始向量化 {len(news_list)} 条新闻...")
    vectorizer = NewsVectorizer()
    
    success = 0
    for i, news in enumerate(news_list, 1):
        try:
            print(f"\n[{i}/{len(news_list)}] {news['title'][:50]}...")
            vectorizer.process_news(**news)
            success += 1
        except Exception as e:
            print(f"❌ 处理失败：{e}")
    
    print(f"\n✅ 完成！成功：{success}/{len(news_list)}")

def fetch_and_vectorize_news():
    """主函数"""
    print(f"\n📰 开始抓取新闻 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"🔑 API Key: {FINNHUB_API_KEY[:10]}... (Finnhub)")
    print("=" * 60)
    
    # 获取新闻
    news_list = fetch_finnhub_news(symbols=WATCHLIST["stocks_us"][:5])
    
    # 处理并向量化
    process_news(news_list)
    
    print("\n" + "=" * 60)
    print("✅ 新闻抓取和向量化完成!")

if __name__ == "__main__":
    fetch_and_vectorize_news()
