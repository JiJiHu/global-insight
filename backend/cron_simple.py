#!/usr/bin/env python3
"""
Railway Cron 定时任务 - 带详细日志的新闻和市场数据抓取
快速完成，带超时保护
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
    print(f"\n📈 [{datetime.now(BEIJING_TZ)}] 开始抓取市场数据...")
    conn = get_conn()
    if not conn:
        return 0
    
    cur = conn.cursor()
    count = 0
    start_time = datetime.now()
    
    # 1. 美股（8 只）
    print(f"  🇺🇸 美股 ({len(symbols)} 只)...")
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
                if data and 'c' in data and data['c'] > 0:
                    cur.execute("""
                        INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                        VALUES (%s, 'stock', %s, %s, %s, NOW())
                        ON CONFLICT (symbol, type, timestamp) DO UPDATE SET
                            price = EXCLUDED.price,
                            change_percent = EXCLUDED.change_percent,
                            volume = EXCLUDED.volume
                    """, (symbol, data['c'], data['dp'], data.get('v', 0)))
                    count += 1
                    print(f"    ✅ {symbol}: ${data['c']} ({data['dp']:+.2f}%)")
        except Exception as e:
            print(f"    ❌ {symbol} 失败：{e}")
    
    # 2. 加密货币（6 只）
    print(f"  ₿ 加密货币 (6 只)...")
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
                    ON CONFLICT (symbol, type, timestamp) DO UPDATE SET
                        price = EXCLUDED.price,
                        change_percent = EXCLUDED.change_percent
                """, (symbol, info['usd'], info.get('usd_24h_change', 0)))
                count += 1
                print(f"    ✅ {symbol}: ${info['usd']:,.2f} ({info.get('usd_24h_change', 0):+.2f}%)")
    except Exception as e:
        print(f"    ❌ 加密货币失败：{e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"  ✅ 市场数据完成：{count} 条 ({elapsed:.1f}秒)")
    return count

def fetch_news():
    """快速抓取新闻 - 带详细日志"""
    print(f"\n📰 [{datetime.now(BEIJING_TZ)}] 开始抓取新闻...")
    conn = get_conn()
    if not conn:
        print("  ❌ 数据库连接失败")
        return 0
    
    cur = conn.cursor()
    count = 0
    news_list = []  # 批量收集
    start_time = datetime.now()
    
    # 1. Finnhub API (最多 30 条)
    print(f"  📡 请求 Finnhub API (过去 24 小时)...")
    finnhub_start = datetime.now()
    try:
        params = {
            'token': FINNHUB_API_KEY,
            'category': 'general',
            'from': int((datetime.now() - timedelta(days=1)).timestamp()),
            'to': int(datetime.now().timestamp())
        }
        resp = requests.get('https://finnhub.io/api/v1/news', params=params, timeout=5)
        finnhub_time = (datetime.now() - finnhub_start).total_seconds()
        print(f"  Finnhub 响应状态码：{resp.status_code} ({finnhub_time:.1f}秒)")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Finnhub 返回数据：{len(data) if isinstance(data, list) else '非列表'} 条")
            
            if isinstance(data, list):
                finnhub_count = 0
                for item in data[:30]:
                    title = item.get('headline', '')[:500]
                    if not title:
                        continue
                    summary = item.get('summary', '')[:2000] or title
                    url = item.get('url', '')[:500]
                    source = item.get('source', 'Finnhub')
                    published = item.get('datetime', 0)
                    ts = datetime.fromtimestamp(published, tz=timezone.utc).isoformat() if published else datetime.now(timezone.utc).isoformat()
                    news_list.append((title, summary, source, url, ts))
                    finnhub_count += 1
                
                print(f"  ✅ Finnhub 收集：{finnhub_count} 条")
    except Exception as e:
        print(f"  ❌ Finnhub 失败：{e}")
    
    # 2. RSS 源（每个最多 10 条）
    rss_sources = {
        '🇨🇳 中国新闻网财经': 'https://www.chinanews.com.cn/rss/finance.xml',
        '🇺🇸 Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
    }
    
    for name, url in rss_sources.items():
        print(f"  📡 请求 {name}...")
        rss_start = datetime.now()
        try:
            feed = feedparser.parse(url, timeout=5)
            rss_time = (datetime.now() - rss_start).total_seconds()
            
            if feed.entries:
                rss_count = 0
                for entry in feed.entries[:10]:
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
                
                print(f"  ✅ {name} 收集：{rss_count} 条 ({rss_time:.1f}秒)")
            else:
                print(f"  ⚠️ {name} 无数据")
        except Exception as e:
            print(f"  ❌ {name} 失败：{e}")
    
    # 批量插入数据库
    if news_list:
        print(f"\n  📦 批量插入 {len(news_list)} 条新闻到数据库...")
        insert_start = datetime.now()
        
        for item in news_list:
            try:
                cur.execute("""
                    INSERT INTO news (title, content, source, url, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        source = EXCLUDED.source
                """, item)
                count += 1
            except Exception as e:
                print(f"    ⚠️ 插入失败：{e}")
        
        conn.commit()
        insert_time = (datetime.now() - insert_start).total_seconds()
        print(f"  ✅ 数据库插入完成：{count} 条 ({insert_time:.1f}秒)")
    else:
        print(f"  ⚠️ 没有新闻数据可插入")
    
    cur.close()
    conn.close()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"  ✅ 新闻抓取完成：{count} 条 ({elapsed:.1f}秒)")
    return count

def main():
    """主函数 - 执行所有任务"""
    print("\n" + "="*60)
    print(f"🕐 Railway Cron 任务 - {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # 执行核心任务
    m_count = fetch_market_data()
    n_count = fetch_news()
    
    print("\n" + "="*60)
    print(f"✅ 全部完成！")
    print(f"   📈 市场数据：{m_count} 条")
    print(f"   📰 新闻：{n_count} 条")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
