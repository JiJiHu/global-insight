#!/usr/bin/env python3
"""
Railway Cron 定时任务 - 简化的新闻和市场数据抓取
只执行核心功能，保证快速完成
"""
import os
import sys
import requests
import feedparser
from datetime import datetime, timezone, timedelta

# 北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
FINNHUB_API_KEY = "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    sys.exit(1)

# 使用原生 psycopg2 连接（更快）
import psycopg2

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def fetch_market_data():
    """快速抓取市场数据"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取市场数据...")
    conn = get_conn()
    cur = conn.cursor()
    count = 0
    
    # 1. 美股（8 只）
    symbols = ["AAPL", "TSLA", "NVDA", "GOOGL", "MSFT", "AMD", "META", "AMZN"]
    for symbol in symbols:
        try:
            resp = requests.get(
                f"https://finnhub.io/api/v1/quote",
                params={"symbol": symbol, "token": FINNHUB_API_KEY},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                if data and 'c' in data:
                    cur.execute("""
                        INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                        VALUES (%s, 'stock', %s, %s, %s, NOW())
                    """, (symbol, data['c'], data['dp'], data.get('v', 0)))
                    count += 1
        except:
            pass
    
    # 2. 加密货币（6 只）
    crypto_map = {"bitcoin": "BTC", "ethereum": "ETH", "cardano": "ADA", 
                  "dogecoin": "DOGE", "solana": "SOL", "tether": "USDT"}
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum,cardano,dogecoin,solana,tether",
                   "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=10
        )
        if resp.status_code == 200:
            for coin_id, info in resp.json().items():
                symbol = crypto_map.get(coin_id, coin_id.upper())
                cur.execute("""
                    INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                    VALUES (%s, 'crypto', %s, %s, 0, NOW())
                """, (symbol, info['usd'], info.get('usd_24h_change', 0)))
                count += 1
    except:
        pass
    
    # 3. 黄金和石油
    try:
        resp = requests.get(
            "https://api.metals.dev/v1/latest",
            params={"api_key": "demo", "symbols": "XAU"},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            if 'metals' in data and 'XAU' in data['metals']:
                cur.execute("""
                    INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                    VALUES ('XAU', 'gold', %s, 0, 0, NOW())
                """, (data['metals']['XAU'].get('price', 600),))
                count += 1
    except:
        pass
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"  ✅ 市场数据：{count} 条")
    return count

def fetch_news():
    """快速抓取新闻"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取新闻...")
    conn = get_conn()
    cur = conn.cursor()
    count = 0
    
    # 1. Finnhub API (最多 30 条)
    try:
        from datetime import timedelta
        params = {
            'token': FINNHUB_API_KEY,
            'category': 'general',
            'from': int((datetime.now() - timedelta(days=1)).timestamp()),
            'to': int(datetime.now().timestamp())
        }
        resp = requests.get('https://finnhub.io/api/v1/news', params=params, timeout=10)
        if resp.status_code == 200:
            for item in resp.json()[:30]:
                title = item.get('headline', '')[:500]
                if not title:
                    continue
                summary = item.get('summary', '')[:2000] or title
                url = item.get('url', '')[:500]
                source = item.get('source', 'Finnhub')
                published = item.get('datetime', 0)
                ts = datetime.fromtimestamp(published, tz=timezone.utc).isoformat()
                
                cur.execute("""
                    INSERT INTO news (title, content, source, url, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (title, summary, source, url, ts))
                count += 1
    except Exception as e:
        print(f"  ❌ Finnhub 失败：{e}")
    
    # 2. RSS 源（每个最多 10 条）
    rss_sources = {
        '中国新闻网财经': 'https://www.chinanews.com.cn/rss/finance.xml',
        'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
    }
    
    for name, url in rss_sources.items():
        try:
            feed = feedparser.parse(url, timeout=10)
            for entry in feed.entries[:10]:
                title = entry.title[:500]
                summary = entry.get('description', '')[:2000] or title
                link = entry.get('link', '')[:500]
                pub_date = entry.get('published', '')
                
                try:
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                    ts = dt.isoformat()
                except:
                    ts = datetime.now(timezone.utc).isoformat()
                
                cur.execute("""
                    INSERT INTO news (title, content, source, url, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (title, summary, name, link, ts))
                count += 1
        except:
            pass
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"  ✅ 新闻：{count} 条")
    return count

def main():
    """主函数 - 执行所有任务"""
    print("\n" + "="*50)
    print(f"🕐 Cron 任务开始 - {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")
    
    # 只执行核心任务
    m_count = fetch_market_data()
    n_count = fetch_news()
    
    print("\n" + "="*50)
    print(f"✅ 完成！市场数据 {m_count} 条，新闻 {n_count} 条")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
