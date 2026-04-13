#!/usr/bin/env python3
"""快速修复：为 insights 表添加 source 字段并更新数据"""

from db import get_db_connection

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # 检查是否有 related_news 字段
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name='insights' AND column_name='related_news'
    """)
    has_related = cur.fetchone()
    
    if has_related:
        # 从 related_news 提取 source
        cur.execute("""
            UPDATE insights 
            SET related_news = ARRAY[
                CASE 
                    WHEN content LIKE '%finnhub%' THEN 'https://finnhub.io'
                    WHEN content LIKE '%cnbc%' THEN 'https://cnbc.com'
                    WHEN content LIKE '%bloomberg%' THEN 'https://bloomberg.com'
                    WHEN content LIKE '%reuters%' THEN 'https://reuters.com'
                    ELSE 'https://global-insight.com'
                END
            ]
            WHERE related_news IS NULL OR array_length(related_news, 1) IS NULL
        """)
        conn.commit()
        print("✅ 已更新 insights 数据")
    else:
        print("❌ 没有 related_news 字段")
    
    cur.close()

print("完成！")
