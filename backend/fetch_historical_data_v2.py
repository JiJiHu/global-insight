#!/usr/bin/env python3
"""
循环抓取市场数据 - 快速生成历史数据（短版本）
"""
import sys
import time
from datetime import datetime, timedelta
sys.path.insert(0, '/app')

from fetch_market_data import fetch_all_market_data
from db import get_db_connection

def fetch_historical_data(days=2, fetches_per_day=12):
    """
    抓取历史数据
    days: 天数
    fetches_per_day: 每天抓取次数（12次 = 每2小时一次）
    """
    print(f"🚀 开始生成 {days} 天的历史数据（每天 {fetches_per_day} 次抓取）")

    current_time = datetime.now()
    total_fetches = days * fetches_per_day

    for fetch_num in range(total_fetches):
        # 计算模拟的历史时间
        days_back = fetch_num // fetches_per_day
        hours_back = (fetch_num % fetches_per_day) * (24 // fetches_per_day)
        simulated_time = current_time - timedelta(days=days_back, hours=hours_back)

        print(f"\n[{fetch_num+1}/{total_fetches}] 模拟时间: {simulated_time.strftime('%Y-%m-%d %H:%M')}")

        # 抓取数据
        fetch_all_market_data()

        # 修改刚插入数据的 timestamp
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE market_data
                SET timestamp = %s
                WHERE id = (
                    SELECT id FROM market_data
                    ORDER BY id DESC LIMIT 1
                )
            """, (simulated_time,))
            conn.commit()
            cur.close()

        # 避免API限流
        if fetch_num < total_fetches - 1:
            time.sleep(5)

    print("\n✅ 历史数据生成完成!")

    # 统计
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM market_data")
        result = cur.fetchone()
        print(f"\n📊 统计：{result[0]} 条数据")
        print(f"   从 {result[1]}")
        print(f"   到 {result[2]}")

if __name__ == "__main__":
    # 生成10天的历史数据，每天12次（每2小时一次）
    fetch_historical_data(days=10, fetches_per_day=12)
