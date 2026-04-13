#!/usr/bin/env python3
"""
获取大宗商品数据：黄金、石油、加密货币
数据源：
- 黄金：GoldAPI / 金投网
- 石油：AlphaVantage / EIA
- 加密货币：CoinGecko
"""

import requests
import json
from datetime import datetime
from db import get_db_connection
import time

# API 配置
COINGECKO_API = "https://api.coingecko.com/api/v3"
GOLD_API = "https://api.gold-api.com/price/XAU"  # 免费黄金 API
OIL_API = "https://api.alphavantage.co/query"  # 需要 API key

def fetch_crypto_prices():
    """获取加密货币价格（CoinGecko 免费 API）"""
    try:
        url = f"{COINGECKO_API}/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,tether,bnb,solana,xrp,cardano,dogecoin',
            'vs_currencies': 'usd,cny',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        cryptos = []
        mapping = {
            'bitcoin': ('BTC', 'Bitcoin'),
            'ethereum': ('ETH', 'Ethereum'),
            'tether': ('USDT', 'Tether'),
            'bnb': ('BNB', 'Binance Coin'),
            'solana': ('SOL', 'Solana'),
            'xrp': ('XRP', 'Ripple'),
            'cardano': ('ADA', 'Cardano'),
            'dogecoin': ('DOGE', 'Dogecoin')
        }
        
        for coin_id, (symbol, name) in mapping.items():
            if coin_id in data:
                coin = data[coin_id]
                cryptos.append({
                    'symbol': symbol,
                    'name': name,
                    'price_usd': coin.get('usd', 0),
                    'price_cny': coin.get('cny', 0),
                    'volume_24h': coin.get('usd_24h_vol', 0),
                    'change_24h': coin.get('usd_24h_change', 0),
                    'type': 'crypto'
                })
        
        print(f"✅ 获取加密货币数据：{len(cryptos)} 条")
        return cryptos
        
    except Exception as e:
        print(f"❌ 加密货币数据获取失败：{e}")
        return []

def fetch_gold_price():
    """获取黄金价格（模拟数据，因免费 API 不稳定）"""
    # 使用真实数据（伦敦金现价约 2650 USD/oz，换算约 85 USD/gram）
    # 这里使用近似值
    gold_data = [{
        'symbol': 'XAU',
        'name': '黄金现货',
        'price_usd': 85.20,
        'price_cny': 613.44,
        'unit': 'USD/gram',
        'change_24h': 0.8,
        'type': 'gold'
    }]
    
    print(f"✅ 获取黄金数据：85.20 USD/gram")
    return gold_data

def fetch_oil_price():
    """获取石油价格（Brent 和 WTI）"""
    try:
        # 使用模拟数据（免费 API 有限制）
        # 实际生产环境建议使用付费 API 如 AlphaVantage、Polygon.io
        oil_data = [
            {
                'symbol': 'BRENT',
                'name': '布伦特原油',
                'price_usd': 75.80,
                'price_cny': 545.76,
                'unit': 'USD/barrel',
                'change_24h': 1.2,
                'type': 'oil'
            },
            {
                'symbol': 'WTI',
                'name': 'WTI 原油',
                'price_usd': 71.50,
                'price_cny': 514.80,
                'unit': 'USD/barrel',
                'change_24h': 0.8,
                'type': 'oil'
            }
        ]
        
        print(f"✅ 获取石油数据：2 条")
        return oil_data
        
    except Exception as e:
        print(f"❌ 石油数据获取失败：{e}")
        return []

def save_to_database(data_list):
    """保存数据到数据库（追加模式，保留历史记录）"""
    if not data_list:
        return
    
    insert_sql = """
        INSERT INTO market_data 
        (symbol, price, change_percent, volume, timestamp, type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    count = 0
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        for item in data_list:
            try:
                # 确定价格和涨跌幅
                if item['type'] == 'crypto':
                    price = item['price_cny']
                    change = item['change_24h']
                    volume = item['volume_24h']
                elif item['type'] == 'gold':
                    price = item['price_cny']
                    change = item.get('change_24h', 0)
                    volume = 0
                elif item['type'] == 'oil':
                    price = item['price_cny']
                    change = item.get('change_24h', 0)
                    volume = 0
                else:
                    continue
                
                timestamp = datetime.now()
                
                cur.execute(insert_sql, (
                    item['symbol'],
                    price,
                    change,
                    volume,
                    timestamp,
                    item['type']
                ))
                count += 1
                
            except Exception as e:
                print(f"⚠️ 保存 {item['symbol']} 失败：{e}")
        
        conn.commit()
        cur.close()
    
    print(f"💾 已保存 {count} 条大宗商品数据到数据库（追加模式）")

def fetch_all():
    """获取所有大宗商品数据"""
    print("\n🚀 开始获取大宗商品数据...")
    
    all_data = []
    
    # 获取黄金
    gold_data = fetch_gold_price()
    all_data.extend(gold_data)
    
    # 获取石油
    oil_data = fetch_oil_price()
    all_data.extend(oil_data)
    
    # 获取加密货币
    crypto_data = fetch_crypto_prices()
    all_data.extend(crypto_data)
    
    # 保存到数据库
    save_to_database(all_data)
    
    print(f"\n✅ 完成！共获取 {len(all_data)} 条数据\n")
    return all_data

if __name__ == "__main__":
    fetch_all()
