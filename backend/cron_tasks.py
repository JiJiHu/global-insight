#!/usr/bin/env python3
"""
Railway Cron 定时任务 - 抓取市场数据并写入数据库
"""
import os
import sys
import httpx
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
                response = httpx.get(f"https://finnhub.io/api/v1/quote", params={
                    "symbol": symbol,
                    "token": "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"
                })
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
        response = httpx.get("https://api.coingecko.com/api/v3/simple/price", params={
            "ids": "bitcoin,ethereum,cardano,dogecoin,solana,tether",
            "vs_currencies": "usd",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        })
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
    """抓取新闻"""
    print(f"[{datetime.now(timezone.utc)}] 开始抓取新闻...")
    # TODO: 实现新闻抓取
    print(f"[{datetime.now(timezone.utc)}] 新闻抓取完成")

def generate_insights():
    """生成 AI 洞察"""
    print(f"[{datetime.now(timezone.utc)}] 开始生成 AI 洞察...")
    if not DASHSCOPE_API_KEY:
        print("  缺少 DASHSCOPE_API_KEY，跳过 AI 洞察生成")
        return
    # TODO: 实现 AI 洞察生成
    print(f"[{datetime.now(timezone.utc)}] AI 洞察生成完成")

def build_graph():
    """构建知识图谱"""
    print(f"[{datetime.now(timezone.utc)}] 开始构建知识图谱...")
    # TODO: 实现知识图谱构建
    print(f"[{datetime.now(timezone.utc)}] 知识图谱构建完成")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python cron_tasks.py <task_name>")
        print("可用任务：fetch-market, fetch-news, generate-insights, build-graph")
        sys.exit(1)
    
    task = sys.argv[1]
    
    if task == "fetch-market":
        fetch_market_data()
    elif task == "fetch-news":
        fetch_news()
    elif task == "generate-insights":
        generate_insights()
    elif task == "build-graph":
        build_graph()
    else:
        print(f"未知任务：{task}")
        sys.exit(1)
