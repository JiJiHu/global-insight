#!/usr/bin/env python3
"""
测试脚本 - 直接在本地运行新闻抓取
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from vercel_tasks import fetch_news

print("=" * 60)
print("开始测试新闻抓取")
print("=" * 60)

count = fetch_news()

print("=" * 60)
print(f"完成！保存了 {count} 条新闻")
print("=" * 60)
