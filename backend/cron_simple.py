#!/usr/bin/env python3
"""
Railway Cron 定时任务 - 快速版
优化目标：2 分钟内完成
"""
import os
import sys
import signal
import requests
import feedparser
from datetime import datetime, timezone, timedelta

# 设置超时：3 分钟强制退出
def timeout_handler(signum, frame):
    print("⚠️ 超时！强制退出（3 分钟限制）")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(180)  # 3 分钟超时

# 北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# 数据库配置 - 优先使用 DATABASE_PUBLIC_URL (Railway PostgreSQL 公共连接)
DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL")
FINNHUB_API_KEY = "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"

print(f"[{datetime.now(BEIJING_TZ)}] Cron 任务启动...")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    sys.exit(1)

import psycopg2

def get_conn():
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        # 确保表存在
        ensure_tables(conn)
        return conn
    except Exception as e:
        print(f"ERROR: 数据库连接失败 - {e}")
        return None

def ensure_tables(conn):
    """确保数据库表存在"""
    cur = conn.cursor()
    try:
        # 创建 news 表（如果不存在）
        cur.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                source VARCHAR(255),
                url TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        print("  ✅ 数据库表已确认")
    except Exception as e:
        print(f"  ⚠️ 建表警告：{e}")
        conn.rollback()
    finally:
        cur.close()

def fetch_market_data():
    """快速抓取市场数据"""
    print(f"\n📈 开始抓取市场数据...")
    conn = get_conn()
    if not conn:
        return 0
    
    cur = conn.cursor()
    count = 0
    start_time = datetime.now()
    
    # 1. 美股（8 只）
    symbols = ["AAPL", "TSLA", "NVDA", "GOOGL", "MSFT", "AMD", "META", "AMZN"]
    print(f"  🇺🇸 美股 ({len(symbols)} 只)...")
    for symbol in symbols:
        try:
            resp = requests.get(
                f"https://finnhub.io/api/v1/quote",
                params={"symbol": symbol, "token": FINNHUB_API_KEY},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                if data and 'c' in data and data['c'] > 0:
                    cur.execute("""
                        INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                        VALUES (%s, 'stock', %s, %s, %s, NOW())
                    """, (symbol, data['c'], data['dp'], data.get('v', 0)))
                    count += 1
                    print(f"    ✅ {symbol}: ${data['c']} ({data['dp']:+.2f}%)")
        except Exception as e:
            print(f"    ❌ {symbol}: {e}")
    
    # 2. 加密货币（6 只）
    print(f"  ₿ 加密货币 (6 只)...")
    crypto_map = {"bitcoin": "BTC", "ethereum": "ETH", "cardano": "ADA", 
                  "dogecoin": "DOGE", "solana": "SOL", "tether": "USDT"}
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum,cardano,dogecoin,solana,tether",
                   "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=5
        )
        if resp.status_code == 200:
            for coin_id, info in resp.json().items():
                symbol = crypto_map.get(coin_id, coin_id.upper())
                cur.execute("""
                    INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                    VALUES (%s, 'crypto', %s, %s, 0, NOW())
                """, (symbol, info['usd'], info.get('usd_24h_change', 0)))
                count += 1
                print(f"    ✅ {symbol}: ${info['usd']:,.2f} ({info.get('usd_24h_change', 0):+.2f}%)")
    except Exception as e:
        print(f"    ❌ 加密货币：{e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"  ✅ 市场数据完成：{count} 条 ({elapsed:.1f}秒)")
    return count

def fetch_news():
    """快速抓取新闻 - 精简版"""
    print(f"\n📰 开始抓取新闻...")
    conn = get_conn()
    if not conn:
        print("  ❌ 数据库连接失败")
        return 0
    
    cur = conn.cursor()
    count = 0
    news_list = []
    start_time = datetime.now()
    
    # 1. Finnhub API (只取 20 条，加速)
    print(f"  📡 Finnhub API (20 条)...")
    try:
        params = {
            'token': FINNHUB_API_KEY,
            'category': 'general',
            'from': int((datetime.now() - timedelta(days=1)).timestamp()),
            'to': int(datetime.now().timestamp())
        }
        resp = requests.get('https://finnhub.io/api/v1/news', params=params, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                for item in data[:20]:  # 减少到 20 条
                    title = item.get('headline', '')[:500]
                    if not title:
                        continue
                    summary = item.get('summary', '')[:2000] or title
                    url = item.get('url', '')[:500]
                    source = item.get('source', 'Finnhub')
                    published = item.get('datetime', 0)
                    ts = datetime.fromtimestamp(published, tz=timezone.utc).isoformat() if published else datetime.now(timezone.utc).isoformat()
                    news_list.append((title, summary, source, url, ts))
                print(f"  ✅ Finnhub: {len([x for x in data[:20] if x.get('headline')])} 条")
    except Exception as e:
        print(f"  ❌ Finnhub: {e}")
    
    # 2. RSS 源（每个只取 5 条，加速）
    rss_sources = {
        '🇨🇳 中国新闻网': 'https://www.chinanews.com.cn/rss/finance.xml',
        '🇺🇸 Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
    }
    
    for name, url in rss_sources.items():
        print(f"  📡 {name} (5 条)...")
        try:
            # feedparser 不支持 timeout 参数，需要使用其他方式实现超时
            import socket
            socket.setdefaulttimeout(3)
            feed = feedparser.parse(url)
            if feed.entries:
                rss_count = 0
                for entry in feed.entries[:5]:  # 减少到 5 条
                    title = entry.title[:500]
                    summary = entry.get('description', '')[:2000] or title
                    link = entry.get('link', '')[:500]
                    pub_date = entry.get('published', '')
                    try:
                        if pub_date:
                            dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                            ts = dt.isoformat()
                        else:
                            ts = datetime.now(timezone.utc).isoformat()
                    except:
                        ts = datetime.now(timezone.utc).isoformat()
                    news_list.append((title, summary, name, link, ts))
                    rss_count += 1
                print(f"  ✅ {name}: {rss_count} 条")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
    
    # 批量插入 - 使用 ON CONFLICT 跳过重复
    if news_list:
        print(f"  📦 插入数据库 ({len(news_list)} 条)...")
        for i, item in enumerate(news_list):
            try:
                cur.execute("""
                    INSERT INTO news (title, content, source, url, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                """, item)
                if cur.rowcount > 0:
                    count += 1
                else:
                    print(f"    ⏭️ 第 {i+1} 条跳过（重复 URL）")
            except Exception as e:
                print(f"    ❌ 第 {i+1} 条插入失败：{e}")
                print(f"       title: {item[0][:50]}...")
        conn.commit()
        print(f"  ✅ 数据库：{count} 条新增"
    
    cur.close()
    conn.close()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"  ✅ 新闻完成：{count} 条 ({elapsed:.1f}秒)")
    return count

def main():
    """主函数"""
    print("\n" + "="*60)
    print(f"🕐 Railway Cron - {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    m_count = fetch_market_data()
    n_count = fetch_news()
    
    print("\n" + "="*60)
    print(f"✅ 完成！市场数据 {m_count} 条，新闻 {n_count} 条")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
