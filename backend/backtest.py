#!/usr/bin/env python3
"""
简单回测系统
- 基于历史数据回测交易策略
- 计算收益率、夏普比率等指标
"""
import sys
from datetime import datetime, timedelta
from db import get_db_connection
import json

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, symbol: str, start_date: str, end_date: str, initial_capital: float = 100000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
    
    def get_historical_data(self) -> list:
        """获取历史数据"""
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT date, open, high, low, close, volume
                FROM daily_prices
                WHERE symbol = %s
                  AND date BETWEEN %s AND %s
                ORDER BY date
            """, (self.symbol, self.start_date, self.end_date))
            data = cur.fetchall()
            cur.close()
            return data
    
    def run_strategy(self, strategy: str = 'buy_and_hold'):
        """运行策略"""
        print(f"\n📊 回测策略：{strategy}")
        print("=" * 60)
        
        if strategy == 'buy_and_hold':
            self._buy_and_hold()
        elif strategy == 'moving_average':
            self._moving_average_crossover()
        
        self._calculate_metrics()
    
    def _buy_and_hold(self):
        """买入持有策略"""
        print(f"   策略：买入并持有 {self.symbol}")
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT MIN(timestamp), price
                FROM market_data
                WHERE symbol = %s
            """, (self.symbol,))
            result = cur.fetchone()
            
            if result and result[1]:
                buy_date, buy_price = result
                shares = int(self.capital / buy_price)
                self.position = shares
                self.capital -= shares * buy_price
                
                self.trades.append({
                    'type': 'buy',
                    'date': str(buy_date),
                    'price': float(buy_price),
                    'shares': shares
                })
                
                print(f"   ✅ 买入：{shares} 股 @ ${buy_price:.2f}")
            
            cur.close()
    
    def _moving_average_crossover(self):
        """均线交叉策略"""
        print(f"   策略：均线交叉 (MA5/MA20)")
        # TODO: 实现均线策略
        print("   ⏳ 策略实现中...")
    
    def _calculate_metrics(self):
        """计算回测指标"""
        print("\n📈 回测结果:")
        print("-" * 60)
        
        # 获取当前价格
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT price FROM market_data
                WHERE symbol = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (self.symbol,))
            result = cur.fetchone()
            current_price = result[0] if result else 0
            cur.close()
        
        # 计算总资产
        portfolio_value = self.capital + (self.position * current_price)
        total_return = ((portfolio_value - self.initial_capital) / self.initial_capital) * 100
        
        print(f"   初始资金：${self.initial_capital:,.2f}")
        print(f"   当前持仓：{self.position} 股")
        print(f"   现金余额：${self.capital:,.2f}")
        print(f"   当前价格：${current_price:.2f}")
        print(f"   总资产：${portfolio_value:,.2f}")
        print(f"   总收益率：{total_return:+.2f}%")
        
        # 保存结果
        result = {
            'symbol': self.symbol,
            'strategy': 'buy_and_hold',
            'initial_capital': self.initial_capital,
            'final_value': portfolio_value,
            'total_return': round(total_return, 2),
            'position': self.position,
            'cash': round(self.capital, 2),
            'trades': self.trades
        }
        
        # 保存到文件
        with open(f'/root/finance-dashboard/backtest-results/{self.symbol}-backtest.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n✅ 回测报告已保存")
        print("=" * 60)

def run_backtest(symbol: str = 'AAPL', strategy: str = 'buy_and_hold'):
    """运行回测"""
    import os
    os.makedirs('/root/finance-dashboard/backtest-results', exist_ok=True)
    
    engine = BacktestEngine(symbol, '2026-01-01', '2026-03-08')
    engine.run_strategy(strategy)

if __name__ == '__main__':
    print("\n🔬 运行回测测试...")
    run_backtest('AAPL', 'buy_and_hold')
