#!/usr/bin/env python3
"""
主运行脚本 - 定时执行
1. 抓取金融数据
2. 抓取新闻并向量化
3. 生成洞察
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_market_data import fetch_all_market_data
from vectorize_news import NewsVectorizer, TEST_NEWS

def run_daily_pipeline():
    """每日定时任务"""
    print("\n" + "=" * 60)
    print("🚀 开始执行每日数据管道")
    print("=" * 60)
    
    # Step 1: 抓取金融数据
    print("\n📊 Step 1: 抓取金融数据")
    print("-" * 60)
    fetch_all_market_data()
    
    # Step 2: 向量化新闻
    print("\n🧠 Step 2: 向量化新闻")
    print("-" * 60)
    vectorizer = NewsVectorizer()
    vectorizer.process_batch(TEST_NEWS)  # 测试数据，实际应替换为真实新闻
    
    # Step 3: 生成洞察 (TODO)
    print("\n💡 Step 3: 生成洞察")
    print("-" * 60)
    print("⏳ 关联分析功能开发中...")
    
    print("\n" + "=" * 60)
    print("✅ 每日数据管道执行完成!")
    print("=" * 60)

if __name__ == "__main__":
    run_daily_pipeline()
