#!/usr/bin/env python3
"""
创建数据库表结构
"""
import os
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    exit(1)

Base = declarative_base()

class MarketData(Base):
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), index=True)
    price = Column(Float)
    change_percent = Column(Float)
    volume = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    type = Column(String(20))  # stock, crypto, gold, oil

# 创建表
engine = create_engine(DATABASE_URL)
print(f"Connecting to database...")
Base.metadata.create_all(engine)
print(f"✅ Table 'market_data' created successfully!")
