#!/usr/bin/env python3
"""
港股数据抓取脚本
使用 AkShare 获取港股行情数据
"""
import sys
from datetime import datetime
sys.path.insert(0, '/root/finance-dashboard/backend')

from db import get_db_connection

# 港股热门股票池
HK_SHARE_STOCKS = {
    '0700.HK': '腾讯控股',
    '9988.HK': '阿里巴巴',
    '9618.HK': '京东集团',
    '3690.HK': '美团',
    '0005.HK': '汇丰控股',
    '0388.HK': '香港交易所',
    '1810.HK': '小米集团',
    '9888.HK': '百度集团',
    '0941.HK': '中国移动',
    '2318.HK': '中国平安',
}

def fetch_hk_share_data():
    """获取港股数据"""
    print("\n🇭🇰 开始抓取港股数据...")
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
        
        for symbol, name in HK_SHARE_STOCKS.items():
            try:
                print(f"\n📈 抓取：{symbol} ({name})")
                
                # 获取港股实时行情
                stock_code = symbol.split('.')[0]
                
                # 使用东方财富港股接口
                df = ak.stock_hk_spot_em()
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
                """, (symbol, 'hk_share', price, change_percent, volume, datetime.now()))
                
                print(f"   ✅ {name}: HKD${price:.2f} ({change_percent:+.2f}%)")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ 抓取失败：{e}")
                fail_count += 1
        
        conn.commit()
        cur.close()
    
    print("\n" + "=" * 60)
    print(f"✅ 港股数据抓取完成！成功：{success_count}, 失败：{fail_count}")
    print("=" * 60)

if __name__ == '__main__':
    fetch_hk_share_data()
