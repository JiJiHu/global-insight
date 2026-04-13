#!/usr/bin/env python3
"""
清理重复新闻标题
"""
import sys
sys.path.insert(0, '/app')
from db import get_db_connection

def clean_duplicates():
    print("🧹 开始清理重复新闻...")
    print("=" * 70)
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 分批处理，避免事务过大
        batch_size = 50
        total_deleted = 0
        
        while True:
            # 查找重复标题
            cur.execute('''
                SELECT title, MIN(id) as min_id
                FROM news 
                GROUP BY title 
                HAVING COUNT(*) > 1 
                LIMIT %s
            ''', (batch_size,))
            
            duplicates = cur.fetchall()
            
            if not duplicates:
                break
            
            for title, min_id in duplicates:
                # 删除重复项（保留 ID 最小的）
                cur.execute('''
                    DELETE FROM news 
                    WHERE title = %s AND id > %s
                ''', (title, min_id))
                
                deleted = cur.rowcount
                total_deleted += deleted
            
            conn.commit()
            print(f"已清理 {total_deleted} 条重复...")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print(f"✅ 共删除 {total_deleted} 条重复新闻")
        
        # 统计
        cur.execute("SELECT COUNT(*) FROM news")
        total = cur.fetchone()[0]
        print(f"📊 剩余新闻总数：{total}条")
        
        # 再次检查是否还有重复
        cur.execute('''
            SELECT COUNT(*) FROM (
                SELECT title FROM news GROUP BY title HAVING COUNT(*) > 1
            ) as duplicates
        ''')
        remaining_dups = cur.fetchone()[0]
        print(f"⚠️  剩余重复标题数：{remaining_dups}个")
        
        cur.close()
        
        return total_deleted, total, remaining_dups

if __name__ == "__main__":
    clean_duplicates()
