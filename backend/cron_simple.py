#!/usr/bin/env python3
"""
Railway Cron 定时任务 - 简化的新闻和市场数据抓取
只执行核心功能，保证快速完成
"""
import os
import sys
import signal
import requests
import feedparser
from datetime import datetime, timezone, timedelta

# 设置超时：5 分钟强制退出
def timeout_handler(signum, frame):
    print("⚠️ 超时！强制退出（5 分钟限制）")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(300)  # 5 分钟超时

# 北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
FINNHUB_API_KEY = "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"

print(f"[{datetime.now(BEIJING_TZ)}] Cron 任务启动...")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    sys.exit(1)

# 使用原生 psycopg2 连接
import psycopg2

def get_conn():
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        return conn
    except Exception as e:
        print(f"ERROR: 数据库连接失败 - {e}")
        return None

def fetch_market_data():
    """快速抓取市场数据"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取市场数据...")
    conn = get_conn()
    if not conn:
        return 0
    
    cur = conn.cursor()
    count = 0
    
    # 1. 美股（5 只核心股票）
    symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]
    for symbol in symbols:
        try:
            resp = requests.get(
                f"https://finnhub.io/api/v1/quote",
                params={"symbol": symbol, "token": FINNHUB_API_KEY},
                timeout=3  # 缩短超时到 3 秒
            )
            if resp.status_code == 200:
                data = resp.json()
                if data and 'c' in data and data['c'] > 0:
                    cur.execute("""
                        INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                        VALUES (%s, 'stock', %s, %s, %s, NOW())
                        ON CONFLICT DO NOTHING
                    """, (symbol, data['c'], data['dp'], data.get('v', 0)))
                    count += 1
        except Exception as e:
            print(f"  ⚠️ {symbol} 失败: {e}")
    
    # 2. 加密货币（3 只主要的）
    crypto_map = {"bitcoin": "BTC", "ethereum": "ETH", "tether": "USDT"}
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum,tether",
                   "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=5  # 缩短超时到 5 秒
        )
        if resp.status_code == 200:
            for coin_id, info in resp.json().items():
                symbol = crypto_map.get(coin_id, coin_id.upper())
                cur.execute("""
                    INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                    VALUES (%s, 'crypto', %s, %s, 0, NOW())
                    ON CONFLICT DO NOTHING
                """, (symbol, info['usd'], info.get('usd_24h_change', 0)))
                count += 1
    except Exception as e:
        print(f"  ⚠️ 加密货币失败: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"  ✅ 市场数据：{count} 条")
    return count

def fetch_news():
    """快速抓取新闻"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取新闻...")
    conn = get_conn()
    if not conn:
        print("  ❌ 数据库连接失败")
        return 0
    
    cur = conn.cursor()
    count = 0
    
    # 1. Finnhub API (最多 15 条)
    print(f"  📡 请求 Finnhub API...")
    try:
        from datetime import timedelta
        params = {
            'token': FINNHUB_API_KEY,
            'category': 'general',
            'from': int((datetime.now() - timedelta(days=1)).timestamp()),
            'to': int(datetime.now().timestamp())
        }
        resp = requests.get('https://finnhub.io/api/v1/news', params=params, timeout=5)  # 缩短超时
        print(f"  Finnhub 响应状态码：{resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Finnhub 返回数据：{len(data) if isinstance(data, list) else '非列表'} 条")
            if isinstance(data, list):
                for item in data[:15]:  # 只取前 15 条
                    title = item.get('headline', '')[:500]
                    if not title:
                        continue
                    summary = item.get('summary', '')[:2000] or title
                    url = item.get('url', '')[:500]
                    source = item.get('source', 'Finnhub')
                    published = item.get('datetime', 0)
                    if published:
                        ts = datetime.fromtimestamp(published, tz=timezone.utc).isoformat()
                    else:
                        ts = datetime.now(timezone.utc).isoformat()
                    
                    try:
                        cur.execute("""
                            INSERT INTO news (title, content, source, url, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (title, summary, source, url, ts))
                        count += 1
                    except Exception as e:
                        print(f"  ⚠️ 插入失败：{e}")
                print(f"  Finnhub 插入了 {count} 条")
    except Exception as e:
        print(f"  ❌ Finnhub 失败：{e}")
    
    # 2. RSS 源（只抓 1 个源，每个最多 5 条）
    rss_sources = {
        '中国新闻网财经': 'https://www.chinanews.com.cn/rss/finance.xml',
    }
    
    for name, url in rss_sources.items():
        try:
            feed = feedparser.parse(url, timeout=5)  # 缩短超时
            for entry in feed.entries[:5]:  # 只取前 5 条
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
                
                try:
                    cur.execute("""
                        INSERT INTO news (title, content, source, url, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (title, summary, name, link, ts))
                    count += 1
                except:
                    pass
        except Exception as e:
            print(f"  ⚠️ {name} 失败: {e}")
    
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
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
