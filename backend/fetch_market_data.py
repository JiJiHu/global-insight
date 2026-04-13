#!/usr/bin/env python3
"""
金融数据抓取脚本
- Finnhub API (主要，60 次/分钟)
"""
import requests
from datetime import datetime
from config import WATCHLIST, FINNHUB_API_KEY
from db import insert_market_data

BASE_URL = "https://finnhub.io/api/v1"

def fetch_finnhub(endpoint, **params):
    """通用 Finnhub 请求"""
    try:
        params['token'] = FINNHUB_API_KEY
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"   请求失败：{e}")
        return None

def fetch_stock_quote(symbol):
    """获取股票报价 (Finnhub)"""
    data = fetch_finnhub('quote', symbol=symbol)
    if not data or data.get('c') is None:
        return None
    
    price = float(data['c'])  # Current price
    change = float(data['d'])  # Change
    change_percent = float(data['dp'])  # Change percent
    volume = int(data.get('v', 0))  # Volume
    
    return price, change_percent, volume

def fetch_crypto_data(symbol):
    """获取加密货币数据 (Finnhub)"""
    # Finnhub 加密货币格式：BTCUSD=X
    data = fetch_finnhub('crypto/exchange-rate', symbol=symbol)
    if not data or 'rate' not in data:
        return None
    
    price = float(data['rate'])
    return price, 0, 0

def fetch_forex_data(currency):
    """获取汇率数据 (Finnhub)"""
    data = fetch_finnhub('forex/rate', symbol=f"{currency}_USD")
    if not data or 'rate' not in data:
        return None
    
    price = float(data['rate'])
    return price, 0, 0

def fetch_all_market_data():
    """抓取所有监控的金融数据"""
    print(f"\n📊 开始抓取金融数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"🔑 API Key: {FINNHUB_API_KEY[:10]}... (Finnhub)")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    # 美股
    print("\n🇺🇸 美股:")
    for symbol in WATCHLIST["stocks_us"]:
        result = fetch_stock_quote(symbol)
        if result:
            price, change, volume = result
            insert_market_data(symbol, 'stock', price, change, volume)
            print(f"✅ {symbol}: ${price:.2f} ({change:+.2f}%)")
            success_count += 1
        else:
            print(f"❌ {symbol} 失败")
            fail_count += 1
    
    # 加密货币
    print("\n₿ 加密货币:")
    for crypto in WATCHLIST["crypto"]:
        result = fetch_crypto_data(crypto)
        if result:
            price, change, volume = result
            insert_market_data(f"{crypto}", 'crypto', price, change, volume)
            print(f"✅ {crypto}: ${price:.2f}")
            success_count += 1
        else:
            print(f"❌ {crypto} 失败")
            fail_count += 1
    
    # 汇率
    print("\n💱 汇率:")
    for currency in WATCHLIST["forex"]:
        result = fetch_forex_data(currency)
        if result:
            price, change, volume = result
            insert_market_data(f"{currency}/USD", 'forex', price, change, volume)
            print(f"✅ {currency}/USD: {price:.4f}")
            success_count += 1
        else:
            print(f"❌ {currency} 失败")
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！成功：{success_count}, 失败：{fail_count}")
    print(f"💡 数据源：Finnhub API (60 次/分钟)")

if __name__ == "__main__":
    fetch_all_market_data()
