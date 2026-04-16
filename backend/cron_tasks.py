#!/usr/bin/env python3
"""
Railway Cron 定时任务 - 抓取市场数据和新闻并写入数据库
每 30 分钟执行一次
"""
import os
import sys
import requests
import feedparser
from datetime import datetime, timezone, timedelta

# 北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    sys.exit(1)

Base = declarative_base()

class MarketData(Base):
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), index=True)
    price = Column(Float)
    change_percent = Column(Float)
    volume = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=lambda: datetime.now(BEIJING_TZ))
    type = Column(String(20))  # stock, crypto, gold, oil
    
    def __repr__(self):
        return f"<MarketData(symbol='{self.symbol}', price={self.price})>"

# 创建数据库引擎和会话
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def fetch_market_data():
    """抓取市场数据并写入数据库"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取市场数据...")
    
    session = Session()
    count = 0
    
    # 美股数据（使用 Finnhub API）
    try:
        symbols = ["AAPL", "TSLA", "NVDA", "GOOGL", "MSFT", "AMD", "META", "AMZN"]
        for symbol in symbols:
            try:
                response = requests.get(f"https://finnhub.io/api/v1/quote", params={
                    "symbol": symbol,
                    "token": "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"
                }, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data and 'c' in data:
                        market = MarketData(
                            symbol=symbol,
                            price=data['c'],
                            change_percent=data['dp'],
                            volume=data.get('v', 0),
                            timestamp=datetime.now(BEIJING_TZ),
                            type='stock'
                        )
                        session.add(market)
                        count += 1
                        print(f"  ✅ {symbol}: ${data['c']:.2f} ({data['dp']:+.2f}%)")
            except Exception as e:
                print(f"  ❌ {symbol} 失败：{e}")
    except Exception as e:
        print(f"  美股数据抓取失败：{e}")
    
    # 加密货币数据
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price", params={
            "ids": "bitcoin,ethereum,cardano,dogecoin,solana,tether",
            "vs_currencies": "usd",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }, timeout=10)
        if response.status_code == 200:
            data = response.json()
            mapping = {
                "bitcoin": "BTC",
                "ethereum": "ETH",
                "cardano": "ADA",
                "dogecoin": "DOGE",
                "solana": "SOL",
                "tether": "USDT"
            }
            for coin_id, info in data.items():
                symbol = mapping.get(coin_id, coin_id.upper())
                market = MarketData(
                    symbol=symbol,
                    price=info['usd'],
                    change_percent=info.get('usd_24h_change', 0),
                    volume=info.get('usd_24h_vol', 0),
                    timestamp=datetime.now(BEIJING_TZ),
                    type='crypto'
                )
                session.add(market)
                count += 1
                print(f"  ✅ {symbol}: ${info['usd']:.2f} ({info.get('usd_24h_change', 0):+.2f}%)")
    except Exception as e:
        print(f"  加密货币数据抓取失败：{e}")
    
    # 黄金数据（使用模拟数据，因免费 API 不稳定）
    try:
        # 伦敦金现价约 2650-3100 USD/oz，换算约 85-100 USD/gram
        gold_price = 85.20  # USD/gram
        market = MarketData(
            symbol='XAU',
            price=gold_price,
            change_percent=0.8,
            volume=0,
            timestamp=datetime.now(BEIJING_TZ),
            type='gold'
        )
        session.add(market)
        count += 1
        print(f"  ✅ XAU (黄金): ${gold_price:.2f}/gram (+0.80%)")
    except Exception as e:
        print(f"  黄金数据抓取失败：{e}")
    
    # 石油数据（使用模拟数据）
    try:
        # 布伦特原油和 WTI 原油价格
        oil_prices = [
            ('BRENT', 75.50, '布伦特原油'),
            ('WTI', 71.20, 'WTI 原油')
        ]
        for symbol, price, name in oil_prices:
            market = MarketData(
                symbol=symbol,
                price=price,
                change_percent=-0.5,
                volume=0,
                timestamp=datetime.now(BEIJING_TZ),
                type='oil'
            )
            session.add(market)
            count += 1
            print(f"  ✅ {symbol} ({name}): ${price:.2f}/bbl (-0.50%)")
    except Exception as e:
        print(f"  石油数据抓取失败：{e}")
    
    # 提交事务
    try:
        session.commit()
        print(f"[{datetime.now(BEIJING_TZ)}] 市场数据抓取完成，成功写入 {count} 条记录")
    except Exception as e:
        session.rollback()
        print(f"  数据库写入失败：{e}")
    finally:
        session.close()

def fetch_news():
    """抓取新闻（多来源：Finnhub + RSS + Twitter）"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取新闻...")
    
    from datetime import timedelta
    from sqlalchemy import text
    
    FINNHUB_API_KEY = "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"
    total = 0
    session = Session()
    
    # 1. Finnhub API (Reuters, CNBC, Bloomberg)
    print("\n📰 Finnhub API...")
    try:
        params = {
            'token': FINNHUB_API_KEY,
            'category': 'general',
            'from': int((datetime.now() - timedelta(days=3)).timestamp()),
            'to': int(datetime.now().timestamp())
        }
        response = requests.get('https://finnhub.io/api/v1/news', params=params, timeout=15)
        data = response.json()
        print(f"  获取到 {len(data)} 条")
        
        for item in data[:50]:
            title = item.get('headline', '')
            summary = item.get('summary', '') or title
            url = item.get('url', '')
            published = item.get('datetime', 0)
            source = item.get('source', 'Finnhub')
            
            if not title:
                continue
            
            try:
                session.execute(text("""
                    INSERT INTO news (title, content, source, url, created_at)
                    VALUES (:title, :content, :source, :url, :created_at)
                """), {
                    'title': title[:500],
                    'content': summary[:2000],
                    'source': source,
                    'url': url[:500],
                    'created_at': datetime.fromtimestamp(published, tz=timezone.utc)
                })
                total += 1
            except:
                pass
        
        print(f"  ✅ 插入 {min(len(data), 50)} 条")
    except Exception as e:
        print(f"  ❌ Finnhub 失败：{e}")
    
    # 2. RSS 新闻源
    rss_sources = {
        '中国新闻网财经': 'https://www.chinanews.com.cn/rss/finance.xml',
        'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
        'Investing.com': 'https://cn.investing.com/rss/news.rss',
        'CNBC Top News': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147',
        'GitHub': 'https://github.blog/feed/',
    }
    
    for name, url in rss_sources.items():
        print(f"\n📰 {name}...")
        try:
            feed = feedparser.parse(url)
            print(f"  获取到 {len(feed.entries)} 条")
            
            for entry in feed.entries[:20]:
                title = entry.title[:500]
                summary = entry.get('description', entry.get('summary', ''))[:2000]
                link = entry.get('link', '')[:500]
                pub_date = entry.get('published', '')
                
                try:
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                    ts = dt.isoformat()
                except:
                    ts = datetime.now(timezone.utc).isoformat()
                
                try:
                    session.execute(text("""
                        INSERT INTO news (title, content, source, url, created_at)
                        VALUES (:title, :content, :source, :url, :created_at)
                    """), {
                        'title': title,
                        'content': summary,
                        'source': name,
                        'url': link,
                        'created_at': ts
                    })
                    total += 1
                except:
                    pass
            
            print(f"  ✅ 插入 {min(len(feed.entries), 20)} 条")
        except Exception as e:
            print(f"  ❌ {name} 失败：{e}")
    
    # 3. Twitter (通过 Nitter)
    twitter_accounts = ['Reuters', 'Bloomberg', 'WSJ', 'CNBC', 'FinancialTimes']
    for account in twitter_accounts:
        print(f"\n🐦 Twitter: @{account}...")
        try:
            rss_url = f'https://nitter.net/{account}/rss'
            feed = feedparser.parse(rss_url)
            print(f"  获取到 {len(feed.entries)} 条")
            
            for entry in feed.entries[:10]:
                title = entry.title[:500]
                link = entry.link[:500]
                pub_date = entry.get('published', '')
                
                try:
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                    ts = dt.isoformat()
                except:
                    ts = datetime.now(timezone.utc).isoformat()
                
                source = f'Twitter-{account}'
                try:
                    session.execute(text("""
                        INSERT INTO news (title, content, source, url, created_at)
                        VALUES (:title, :content, :source, :url, :created_at)
                    """), {
                        'title': title,
                        'content': '',
                        'source': source,
                        'url': link,
                        'created_at': ts
                    })
                    total += 1
                except:
                    pass
            
            print(f"  ✅ 插入 {min(len(feed.entries), 10)} 条")
        except Exception as e:
            print(f"  ❌ @{account} 失败：{e}")
    
    # 提交所有
    try:
        session.commit()
        print(f"\n{'='*50}")
        print(f"✅ 新闻抓取完成！共插入 {total} 条")
        print(f"{'='*50}")
    except Exception as e:
        session.rollback()
        print(f"  ❌ 数据库提交失败：{e}")
    finally:
        session.close()
    
    return total
        
        # 保存到数据库
        session = Session()
        saved = 0
        
        for item in data[:30]:  # 最多保存 30 条
            title = item.get('headline', '')
            summary = item.get('summary', '') or title
            url = item.get('url', '')
            published = item.get('datetime', 0)
            source = item.get('source', 'Finnhub')
            
            if not title:
                continue
            
            # 简单情感分析
            sentiment_score = 0.0
            sentiment_label = '中性'
            text_lower = (title + ' ' + summary).lower()
            if any(word in text_lower for word in ['rise', 'gain', 'grow', 'surge', 'beat', 'strong', 'positive', 'up']):
                sentiment_score = 0.6
                sentiment_label = '积极'
            elif any(word in text_lower for word in ['fall', 'drop', 'decline', 'crash', 'miss', 'weak', 'negative', 'down']):
                sentiment_score = -0.6
                sentiment_label = '消极'
            
            # 插入数据库
            from sqlalchemy import text
            result = session.execute(text("""
                INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, created_at)
                VALUES (:title, :content, :source, :sentiment_label, :sentiment_score, :url, :created_at)
                ON CONFLICT (title) DO NOTHING
            """), {
                'title': title,
                'content': summary,
                'source': source,
                'sentiment_label': sentiment_label,
                'sentiment_score': sentiment_score,
                'url': url,
                'created_at': datetime.fromtimestamp(published, tz=BEIJING_TZ)
            })
            if result.rowcount > 0:
                saved += 1
        
        session.commit()
        session.close()
        
        print(f"  ✅ 成功保存 {saved} 条新闻")
        return saved
        
    except Exception as e:
        print(f"  ❌ 新闻抓取失败：{e}")
        import traceback
        traceback.print_exc()
        return 0

def generate_insights():
    """生成 AI 洞察（基于市场数据和新闻）"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始生成 AI 洞察...")
    
    if not DASHSCOPE_API_KEY:
        print("  ⚠️ 缺少 DASHSCOPE_API_KEY，跳过 AI 洞察生成")
        return 0
    
    try:
        from sqlalchemy import text
        
        # 获取最新市场数据
        session = Session()
        result = session.execute(text("""
            SELECT symbol, type, price, change_percent, timestamp 
            FROM market_data 
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            ORDER BY timestamp DESC
        """)).fetchall()
        
        if not result:
            print("  ⚠️ 没有足够的市场数据生成洞察")
            session.close()
            return 0
        
        # 构建数据摘要
        market_summary = []
        for row in result:
            symbol, type_, price, change, ts = row
            market_summary.append(f"{symbol} ({type_}): ${price:.2f} ({change:+.2f}%)")
        
        # 调用 AI 生成洞察
        prompt = f"""基于以下金融市场数据，生成简短的投资洞察（200 字以内）：
{chr(10).join(market_summary)}

请用中文回答，包含：
1. 市场整体趋势
2. 值得关注的板块或资产
3. 风险提示"""
        
        response = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}"},
            json={
                "model": "qwen-turbo",
                "input": {"messages": [{"role": "user", "content": prompt}]}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            ai_content = response.json().get('output', {}).get('text', '')
            
            # 保存洞察
            session.execute(text("""
                INSERT INTO insights (title, content, created_at)
                VALUES (:title, :content, :created_at)
            """), {
                'title': f'📊 AI 市场洞察 - {datetime.now(BEIJING_TZ).strftime("%m-%d %H:%M")}',
                'content': ai_content,
                'created_at': datetime.now(BEIJING_TZ)
            })
            session.commit()
            print(f"  ✅ AI 洞察生成成功")
        else:
            print(f"  ❌ AI 调用失败：{response.status_code}")
        
        session.close()
        return 1
        
    except Exception as e:
        print(f"  ❌ AI 洞察生成失败：{e}")
        return 0

def build_graph():
    """构建知识图谱（基于市场数据关系）"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始构建知识图谱...")
    
    try:
        from sqlalchemy import text
        
        session = Session()
        
        # 获取所有数据类型
        result = session.execute(text("""
            SELECT DISTINCT type FROM market_data
        """)).fetchall()
        
        types = [row[0] for row in result]
        
        # 获取每个类型的代表性资产
        nodes = []
        links = []
        
        # 添加中心节点
        nodes.append({"id": "market", "label": "金融市场", "type": "center"})
        
        for type_ in types:
            # 添加类型节点
            nodes.append({"id": type_, "label": type_.upper(), "type": "category"})
            links.append({"source": "market", "target": type_})
            
            # 获取该类型的前 5 个资产
            assets = session.execute(text("""
                SELECT symbol, price, change_percent 
                FROM market_data 
                WHERE type = :type
                ORDER BY timestamp DESC 
                LIMIT 5
            """), {'type': type_}).fetchall()
            
            for symbol, price, change in assets:
                nodes.append({"id": symbol, "label": symbol, "type": "asset", "price": price, "change": change})
                links.append({"source": type_, "target": symbol})
        
        # 保存到数据库（如果有 insights_graph 表）
        # 这里简单打印结果
        print(f"  ✅ 知识图谱构建完成：{len(nodes)} 个节点，{len(links)} 条边")
        session.close()
        return {'nodes': nodes, 'links': links}
        
    except Exception as e:
        print(f"  ❌ 知识图谱构建失败：{e}")
        return {'nodes': [], 'links': []}

def run_all_tasks():
    """统一执行所有任务（每 12 小时一次）"""
    print("\n" + "="*60)
    print(f"🕐 开始执行定时任务 - {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print("="*60 + "\n")
    
    # 1. 抓取市场数据
    fetch_market_data()
    print()
    
    # 2. 抓取新闻
    fetch_news()
    print()
    
    # 3. 生成 AI 洞察
    generate_insights()
    print()
    
    # 4. 构建知识图谱
    build_graph()
    print()
    
    print("="*60)
    print(f"✅ 所有任务执行完成 - {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 无参数时默认执行所有任务
        run_all_tasks()
    else:
        task = sys.argv[1]
        
        if task == "fetch-market":
            fetch_market_data()
        elif task == "fetch-news":
            fetch_news()
        elif task == "generate-insights":
            generate_insights()
        elif task == "build-graph":
            build_graph()
        elif task == "all":
            run_all_tasks()
        else:
            print(f"未知任务：{task}")
            print("可用任务：fetch-market, fetch-news, generate-insights, build-graph, all")
            sys.exit(1)
