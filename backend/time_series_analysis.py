#!/usr/bin/env python3
"""
时间序列分析模块
- 历史图谱对比
- 趋势预测
- 异常检测
"""
import sys
from datetime import datetime, timedelta
from db import get_db_connection
import json

def get_historical_graph(days_ago: int) -> dict:
    """获取历史图谱快照"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取指定日期的数据
        cur.execute("""
            SELECT 
                symbol,
                AVG(price) as avg_price,
                AVG(change_percent) as avg_change,
                SUM(volume) as total_volume
            FROM market_data
            WHERE timestamp >= NOW() - INTERVAL '%s days'
              AND timestamp < NOW() - INTERVAL '%s days'
            GROUP BY symbol
        """, (days_ago + 1, days_ago))
        
        stocks = cur.fetchall()
        
        # 获取新闻统计
        cur.execute("""
            SELECT 
                sentiment_label,
                COUNT(*) as count
            FROM news
            WHERE created_at >= NOW() - INTERVAL '%s days'
              AND created_at < NOW() - INTERVAL '%s days'
            GROUP BY sentiment_label
        """, (days_ago + 1, days_ago))
        
        news_stats = cur.fetchall()
        cur.close()
        
        return {
            'date': (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d'),
            'stocks': [
                {
                    'symbol': row[0],
                    'avg_price': float(row[1]) if row[1] else 0,
                    'avg_change': float(row[2]) if row[2] else 0,
                    'total_volume': int(row[3]) if row[3] else 0
                }
                for row in stocks
            ],
            'news_sentiment': {
                row[0]: row[1] for row in news_stats
            }
        }

def detect_anomalies(threshold: float = 2.0) -> list:
    """检测异常波动"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 检测价格异常
        cur.execute("""
            WITH stats AS (
                SELECT 
                    symbol,
                    AVG(change_percent) as avg_change,
                    STDDEV(change_percent) as stddev_change
                FROM market_data
                WHERE timestamp >= NOW() - INTERVAL '30 days'
                GROUP BY symbol
            ),
            latest AS (
                SELECT DISTINCT ON (symbol)
                    symbol,
                    change_percent,
                    timestamp
                FROM market_data
                ORDER BY symbol, timestamp DESC
            )
            SELECT 
                l.symbol,
                l.change_percent,
                s.avg_change,
                s.stddev_change,
                (l.change_percent - s.avg_change) / NULLIF(s.stddev_change, 0) as z_score
            FROM latest l
            JOIN stats s ON l.symbol = s.symbol
            WHERE ABS((l.change_percent - s.avg_change) / NULLIF(s.stddev_change, 0)) > %s
            ORDER BY ABS((l.change_percent - s.avg_change) / NULLIF(s.stddev_change, 0)) DESC
        """, (threshold,))
        
        anomalies = cur.fetchall()
        cur.close()
        
        return [
            {
                'symbol': row[0],
                'current_change': float(row[1]),
                'avg_change': float(row[2]) if row[2] else 0,
                'stddev': float(row[3]) if row[3] else 0,
                'z_score': float(row[4]) if row[4] else 0,
                'severity': 'high' if abs(row[4]) > 3 else 'medium'
            }
            for row in anomalies
        ]

def get_trend_prediction(symbol: str, days: int = 7) -> dict:
    """简单趋势预测"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取历史数据
        cur.execute("""
            SELECT 
                DATE(timestamp) as date,
                AVG(price) as avg_price,
                AVG(change_percent) as avg_change
            FROM market_data
            WHERE symbol = %s
              AND timestamp >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT %s
        """, (symbol, days))
        
        history = cur.fetchall()
        cur.close()
        
        if len(history) < 2:
            return {'error': '数据不足'}
        
        # 简单线性回归预测
        prices = [float(row[1]) for row in reversed(history)]
        n = len(prices)
        
        # 计算斜率
        x_mean = (n - 1) / 2
        y_mean = sum(prices) / n
        
        numerator = sum((i - x_mean) * (prices[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # 预测未来 3 天
        predictions = []
        for i in range(1, 4):
            pred_price = slope * (n - 1 + i) + intercept
            predictions.append({
                'day': i,
                'predicted_price': round(pred_price, 2),
                'trend': 'up' if slope > 0 else 'down'
            })
        
        return {
            'symbol': symbol,
            'history': [
                {'date': str(row[0]), 'price': float(row[1]), 'change': float(row[2]) if row[2] else 0}
                for row in history
            ],
            'slope': round(slope, 4),
            'predictions': predictions,
            'overall_trend': 'upward' if slope > 0 else 'downward'
        }

def analyze_time_series():
    """主函数：执行时间序列分析"""
    print("\n📈 执行时间序列分析...")
    print("=" * 60)
    
    # 1. 异常检测
    print("\n1️⃣ 检测异常波动...")
    anomalies = detect_anomalies(threshold=2.0)
    if anomalies:
        print(f"   发现 {len(anomalies)} 个异常:")
        for anomaly in anomalies[:5]:
            print(f"     - {anomaly['symbol']}: Z-Score={anomaly['z_score']:.2f} ({anomaly['severity']})")
    else:
        print("   ✅ 无异常波动")
    
    # 2. 趋势预测
    print("\n2️⃣ 趋势预测 (TOP3 热门股票)...")
    for symbol in ['GOOGL', 'BTC-USD', 'META']:
        prediction = get_trend_prediction(symbol)
        if 'error' not in prediction:
            trend = prediction['overall_trend']
            print(f"   - {symbol}: {trend} (斜率：{prediction['slope']:.4f})")
    
    print("\n✅ 时间序列分析完成")
    print("=" * 60)

if __name__ == '__main__':
    analyze_time_series()
