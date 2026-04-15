#!/usr/bin/env python3
"""
手动插入黄金和石油数据到数据库
用于快速测试，之后会由 cron_tasks.py 自动更新
"""
import os
import sys
from datetime import datetime, timezone, timedelta

# 北京时间
BEIJING_TZ = timezone(timedelta(hours=8))

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class MarketData(Base):
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), index=True)
    price = Column(Float)
    change_percent = Column(Float)
    volume = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=lambda: datetime.now(BEIJING_TZ))
    type = Column(String(20))

# 从环境变量获取数据库 URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 插入黄金数据
gold_data = [
    ('XAU', 85.20, 0.8, 'gold', '黄金现货'),
    ('BRENT', 75.50, -0.5, 'oil', '布伦特原油'),
    ('WTI', 71.20, -0.5, 'oil', 'WTI 原油'),
]

print(f"开始插入大宗商品数据...")
for symbol, price, change, type_, name in gold_data:
    market = MarketData(
        symbol=symbol,
        price=price,
        change_percent=change,
        volume=0,
        timestamp=datetime.now(BEIJING_TZ),
        type=type_
    )
    session.add(market)
    print(f"  ✅ {symbol} ({name}): ${price:.2f} ({change:+.1f}%)")

session.commit()
session.close()

print(f"\n完成！已插入 {len(gold_data)} 条记录。")
