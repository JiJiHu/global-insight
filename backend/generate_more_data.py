#!/usr/bin/env python3
"""
快速生成更多市场数据
"""
import sys
import random
from datetime import datetime, timedelta
sys.path.insert(0, '/app')
from db import get_db_connection

# 基础数据
BASE_DATA = {
    'stocks': [
        {'symbol': 'AAPL', 'price': 261.0},
        {'symbol': 'TSLA', 'price': 413.0},
        {'symbol': 'NVDA', 'price': 187.5},
        {'symbol': 'GOOGL', 'price': 310.0},
        {'symbol': 'MSFT', 'price': 406.0},
        {'symbol': 'AMD', 'price': 207.5},
        {'symbol': 'META', 'price': 656.0},
        {'symbol': 'AMZN', 'price': 215.0},
    ],
    'crypto': [
        {'symbol': 'BTC', 'price': 98500.0},
        {'symbol': 'ETH', 'price': 2850.0},
        {'symbol': 'ADA', 'price': 1.78},
        {'symbol': 'DOGE', 'price': 0.64},
        {'symbol': 'SOL', 'price': 587.78},
        {'symbol': 'USDT', 'price': 6.86},
    ],
    'gold': [
        {'symbol': 'XAU', 'price': 613.44},
    ],
    'oil': [
        {'symbol': 'BRENT', 'price': 545.76},
        {'symbol': 'WTI', 'price': 514.80},
    ]
}

def generate_price_change():
    """生成随机价格变化 -2% 到 +2%"""
    return random.uniform(-2.0, 2.0)

def insert_historical_data(days=30, hourly=True):
    """
    生成历史数据
    days: 天数
    hourly: 是否每小时一次（否则每10分钟）
    """
    print(f"🚀 开始生成 {days} 天的历史数据")

    interval_minutes = 10 if hourly else 60
    total_points = int(days * 24 * 60 / interval_minutes)
    print(f"   目标：约 {total_points} 条数据/每个标的")

    with get_db_connection() as conn:
        cur = conn.cursor()
        current_time = datetime.now()

        for day in range(days):
            for hour in range(24):
                if hourly or hour % 6 == 0:  # 每小时或每6小时
                    for minute in [0, 10, 20, 30, 40, 50] if not hourly else [0]:
                        if not hourly and minute % (60 // interval_minutes) != 0:
                            continue

                        simulated_time = current_time - timedelta(
                            days=day, hours=hour, minutes=minute
                        )

                        # 股票
                        for stock in BASE_DATA['stocks']:
                            price_change = generate_price_change()
                            new_price = stock['price'] * (1 + price_change / 100)

                            cur.execute("""
                                INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (title) DO NOTHING
                            """, (
                                stock['symbol'], 'stock', new_price, price_change,
                                random.randint(20000000, 100000000), simulated_time
                            ))

                        # 加密货币
                        for crypto in BASE_DATA['crypto']:
                            price_change = generate_price_change()
                            new_price = crypto['price'] * (1 + price_change / 100)

                            cur.execute("""
                                INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (title) DO NOTHING
                            """, (
                                crypto['symbol'], 'crypto', new_price, price_change,
                                random.randint(100000, 5000000), simulated_time
                            ))

                        # 黄金
                        for gold in BASE_DATA['gold']:
                            price_change = random.uniform(-0.5, 0.5)
                            new_price = gold['price'] * (1 + price_change / 100)

                            cur.execute("""
                                INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (title) DO NOTHING
                            """, (
                                gold['symbol'], 'gold', new_price, price_change,
                                random.randint(1000000, 10000000), simulated_time
                            ))

                        # 石油
                        for oil in BASE_DATA['oil']:
                            price_change = random.uniform(-1.0, 1.0)
                            new_price = oil['price'] * (1 + price_change / 100)

                            cur.execute("""
                                INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (title) DO NOTHING
                            """, (
                                oil['symbol'], 'oil', new_price, price_change,
                                random.randint(500000, 5000000), simulated_time
                            ))

            conn.commit()
            if (day + 1) % 5 == 0:
                print(f"   ✅ 第 {day + 1}/{days} 天完成")

    print("✅ 历史数据生成完成!")

    # 统计
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM market_data")
        total = cur.fetchone()[0]
        cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM market_data")
        min_t, max_t = cur.fetchone()
        print(f"\n📊 统计：{total} 条数据")
        print(f"   从 {min_t}")
        print(f"   到 {max_t}")

if __name__ == "__main__":
    # 生成 30 天的数据，每 10 分钟一次
    insert_historical_data(days=30, hourly=False)
