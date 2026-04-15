#!/usr/bin/env python3
"""
简化的新闻抓取 - 用于调试
"""
import os
import requests
from datetime import datetime, timezone, timedelta
from db import get_db_connection

BEIJING_TZ = timezone(timedelta(hours=8))

def fetch_news_debug():
    """抓取新闻并打印详细调试信息"""
    print(f"[{datetime.now(BEIJING_TZ)}] 开始抓取新闻...")
    
    # 1. 获取新闻
    response = requests.get("https://finnhub.io/api/v1/news", params={
        "category": "general",
        "token": "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"
    }, timeout=10)
    
    print(f"API 状态码：{response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ API 请求失败")
        return 0
    
    data = response.json()
    print(f"获取到 {len(data) if isinstance(data, list) else 0} 条新闻")
    
    if not isinstance(data, list) or len(data) == 0:
        return 0
    
    # 2. 连接数据库
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 3. 检查数据库连接
        cur.execute("SELECT 1")
        print(f"✅ 数据库连接正常")
        
        # 4. 检查当前新闻总数
        cur.execute("SELECT COUNT(*) FROM news")
        print(f"当前新闻总数：{cur.fetchone()[0]}")
        
        # 5. 尝试插入第一条新闻
        item = data[0]
        title = item.get('headline', '')
        summary = item.get('summary', '') or title
        url = item.get('url', '')
        published = item.get('datetime', 0)
        source = item.get('source', 'Finnhub')
        
        print(f"\n尝试插入第一条新闻:")
        print(f"  标题：{title[:80]}...")
        print(f"  URL: {url[:80]}...")
        print(f"  时间：{datetime.fromtimestamp(published, tz=BEIJING_TZ) if published else 'N/A'}")
        
        # 检查 URL 是否存在
        cur.execute("SELECT id FROM news WHERE url = %s LIMIT 1", (url,))
        exists = cur.fetchone()
        print(f"  URL 是否存在：{'是' if exists else '否'}")
        
        if not exists:
            # 尝试插入
            try:
                cur.execute("""
                    INSERT INTO news (title, content, source, sentiment_label, sentiment_score, url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    title,
                    summary,
                    source,
                    '中性',
                    0.0,
                    url,
                    datetime.fromtimestamp(published, tz=BEIJING_TZ) if published else datetime.now(BEIJING_TZ)
                ))
                print(f"✅ 插入成功，影响行数：{cur.rowcount}")
                
                conn.commit()
                print(f"✅ 事务已提交")
                
                # 验证插入
                cur.execute("SELECT COUNT(*) FROM news")
                print(f"✅ 插入后新闻总数：{cur.fetchone()[0]}")
                
            except Exception as e:
                print(f"❌ 插入失败：{e}")
                conn.rollback()
        else:
            print(f"⚠️ URL 已存在，跳过")
        
        cur.close()
    
    return 1 if not exists else 0

if __name__ == "__main__":
    fetch_news_debug()
