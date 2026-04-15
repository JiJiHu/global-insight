#!/usr/bin/env python3
"""
诊断脚本 - 检查新闻重复问题
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from db import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

# 检查新闻总数
cur.execute("SELECT COUNT(*) FROM news")
print(f"新闻总数：{cur.fetchone()[0]}")

# 检查最新 10 条新闻
cur.execute("""
    SELECT title, source, created_at 
    FROM news 
    ORDER BY created_at DESC 
    LIMIT 10
""")
print("\n最新 10 条新闻:")
for row in cur.fetchall():
    print(f"  - {row[0][:60]}... | {row[1]} | {row[2]}")

# 检查是否有今天的新闻
cur.execute("""
    SELECT COUNT(*) 
    FROM news 
    WHERE created_at >= NOW() - INTERVAL '1 day'
""")
today_count = cur.fetchone()[0]
print(f"\n今日新闻数量：{today_count}")

# 检查是否有重复标题
cur.execute("""
    SELECT title, COUNT(*) as cnt
    FROM news
    GROUP BY title
    HAVING COUNT(*) > 1
    LIMIT 5
""")
dups = cur.fetchall()
if dups:
    print("\n重复标题示例:")
    for row in dups:
        print(f"  - {row[0][:60]}... ({row[1]}次)")
else:
    print("\n✅ 没有重复标题")

cur.close()
conn.close()
