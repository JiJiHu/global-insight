#!/usr/bin/env python3
"""
A 股数据抓取脚本
使用 AkShare 获取 A 股行情数据
"""
import sys
import pandas as pd
from datetime import datetime
sys.path.insert(0, '/root/finance-dashboard/backend')

from db import get_db_connection

# A 股热门股票池
A_SHARE_STOCKS = {
    '600519.SS': '贵州茅台',
    '000858.SZ': '五粮液',
    '300750.SZ': '宁德时代',
    '601318.SS': '中国平安',
    '600036.SS': '招商银行',
    '000333.SZ': '美的集团',
    '601888.SS': '中国中免',
    '002415.SZ': '海康威视',
    '600276.SS': '恒瑞医药',
    '601899.SS': '紫金矿业',
}

def fetch_a_share_data():
    """获取 A 股数据"""
    print("\n🇨🇳 开始抓取 A 股数据...")
    print("=" * 60)
    
    try:
        import akshare as ak
    except ImportError:
        print("⚠️  未安装 akshare，请先安装：pip install akshare")
        return
    
    success_count = 0
    fail_count = 0
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        for symbol, name in A_SHARE_STOCKS.items():
            try:
                print(f"\n📈 抓取：{symbol} ({name})")
                
                # 获取实时行情（使用东方财富接口）
                stock_code = symbol.split('.')[0]
                market = 'sh' if symbol.endswith('.SS') else 'sz'
                
                # 获取实时行情
                df = ak.stock_zh_a_spot_em()
                stock_data = df[df['代码'] == stock_code]
                
                if stock_data.empty:
                    print(f"   ⚠️  未找到数据")
                    fail_count += 1
                    continue
                
                row = stock_data.iloc[0]
                price = float(row['最新价'])
                change_percent = float(row['涨跌幅'])
                volume = int(float(row['成交量']) * 100)  # 手转股
                
                # 插入数据库
                cur.execute("""
                    INSERT INTO market_data (symbol, type, price, change_percent, volume, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timestamp) DO UPDATE SET
                        price = EXCLUDED.price,
                        change_percent = EXCLUDED.change_percent,
                        volume = EXCLUDED.volume
                """, (symbol, 'a_share', price, change_percent, volume, datetime.now()))
                
                print(f"   ✅ {name}: ¥{price:.2f} ({change_percent:+.2f}%)")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ 抓取失败：{e}")
                fail_count += 1
        
        conn.commit()
        cur.close()
    
    print("\n" + "=" * 60)
    print(f"✅ A 股数据抓取完成！成功：{success_count}, 失败：{fail_count}")
    print("=" * 60)

if __name__ == '__main__':
    fetch_a_share_data()
