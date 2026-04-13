#!/usr/bin/env python3
"""
AI 周报生成器
- 每周自动生成市场总结报告
- 包含：市场表现、热门股票、新闻分析、AI 洞察
"""
import sys
from datetime import datetime, timedelta
from db import get_db_connection
import json

def generate_weekly_report():
    """生成周报"""
    print("\n📊 生成 AI 周报...")
    print("=" * 60)
    
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())  # 本周一
    report_date = week_start.strftime('%Y-%m-%d')
    
    report = {
        'title': f'📈 金融市场周报 | {report_date}',
        'sections': []
    }
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 1. 市场整体表现
        print("\n1️⃣ 分析市场整体表现...")
        cur.execute("""
            SELECT 
                COUNT(DISTINCT symbol) as total_symbols,
                AVG(change_percent) as avg_change,
                MAX(change_percent) as best_gain,
                MIN(change_percent) as worst_loss,
                SUM(volume) as total_volume
            FROM (
                SELECT DISTINCT ON (symbol)
                    symbol, change_percent, volume
                FROM market_data
                WHERE timestamp >= NOW() - INTERVAL '7 days'
                ORDER BY symbol, timestamp DESC
            ) latest
        """)
        market_stats = cur.fetchone()
        
        if market_stats[0]:
            total_symbols, avg_change, best_gain, worst_loss, total_volume = market_stats
            
            # 判断市场情绪
            if avg_change > 2:
                sentiment = "🟢 积极"
            elif avg_change < -2:
                sentiment = "🔴 消极"
            else:
                sentiment = "🟡 震荡"
            
            section = {
                'title': '📊 市场整体表现',
                'content': f"""
本周市场整体{sentiment}。

- **监控股票**: {total_symbols} 只
- **平均涨跌幅**: {avg_change:+.2f}%
- **最佳表现**: +{best_gain:.2f}%
- **最差表现**: {worst_loss:.2f}%
- **总成交量**: {total_volume:,.0f}
"""
            }
            report['sections'].append(section)
            print(f"   ✅ 平均涨跌：{avg_change:+.2f}%")
        
        # 2. 热门股票（被新闻提及最多）
        print("\n2️⃣ 分析热门股票...")
        cur.execute("""
            SELECT 
                UNNEST(related_symbols) as symbol,
                COUNT(*) as mention_count
            FROM news
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY UNNEST(related_symbols)
            ORDER BY mention_count DESC
            LIMIT 5
        """)
        hot_stocks = cur.fetchall()
        
        if hot_stocks:
            section = {
                'title': '🔥 热门股票 TOP5',
                'content': '\n'.join([
                    f"{i+1}. **{row[0]}**: {row[1]} 次提及"
                    for i, row in enumerate(hot_stocks)
                ])
            }
            report['sections'].append(section)
            print(f"   ✅ 最热股票：{hot_stocks[0][0]} ({hot_stocks[0][1]} 次)")
        
        # 3. 新闻情感分析
        print("\n3️⃣ 分析新闻情感...")
        cur.execute("""
            SELECT 
                sentiment_label,
                COUNT(*) as count
            FROM news
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY sentiment_label
            ORDER BY count DESC
        """)
        sentiment_stats = cur.fetchall()
        
        if sentiment_stats:
            total_news = sum(row[1] for row in sentiment_stats)
            sentiment_content = "\n".join([
                f"- {row[0]}: {row[1]} 条 ({row[1]/total_news*100:.1f}%)"
                for row in sentiment_stats
            ])
            
            section = {
                'title': '📰 新闻情感分析',
                'content': f"""
本周共 {total_news} 条新闻。

{sentiment_content}
"""
            }
            report['sections'].append(section)
            print(f"   ✅ 新闻总数：{total_news} 条")
        
        # 4. AI 洞察总结
        print("\n4️⃣ 总结 AI 洞察...")
        cur.execute("""
            SELECT 
                analysis_type,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence
            FROM insights
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY analysis_type
        """)
        insight_stats = cur.fetchall()
        
        if insight_stats:
            section = {
                'title': '💡 AI 洞察',
                'content': '\n'.join([
                    f"- {row[0]}: {row[1]} 条 (置信度：{row[2]*100:.0f}%)"
                    for row in insight_stats
                ])
            }
            report['sections'].append(section)
            print(f"   ✅ 洞察类型：{len(insight_stats)} 种")
        
        # 5. 重点新闻
        print("\n5️⃣ 提取重点新闻...")
        cur.execute("""
            SELECT title, sentiment_label, source
            FROM news
            WHERE created_at >= NOW() - INTERVAL '7 days'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        top_news = cur.fetchall()
        
        if top_news:
            section = {
                'title': '📌 重点新闻',
                'content': '\n'.join([
                    f"{i+1}. {row[0]} ({row[1]})"
                    for i, row in enumerate(top_news)
                ])
            }
            report['sections'].append(section)
            print(f"   ✅ 重点新闻：{len(top_news)} 条")
        
        cur.close()
    
    # 6. 投资建议
    print("\n6️⃣ 生成投资建议...")
    report['sections'].append({
        'title': '💼 投资建议',
        'content': """
⚠️ **风险提示**: 本报告仅供参考，不构成投资建议。

**建议关注**:
1. 密切关注市场情绪变化
2. 分散投资，降低风险
3. 关注热门股票的后续动向
4. 定期查看 AI 洞察更新
"""
    })
    
    # 生成最终报告
    report_text = f"# {report['title']}\n\n"
    report_text += f"**生成时间**: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report_text += "---\n\n"
    
    for section in report['sections']:
        report_text += f"## {section['title']}\n\n"
        report_text += section['content'] + "\n\n"
    
    report_text += "---\n"
    report_text += "*报告由 AI 自动生成 | 数据仅供参考*\n"
    
    # 保存报告
    report_file = f'/root/finance-dashboard/reports/weekly-report-{report_date}.md'
    import os
    os.makedirs('/root/finance-dashboard/reports', exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"\n✅ 周报已保存：{report_file}")
    print("=" * 60)
    
    return report_file

if __name__ == '__main__':
    generate_weekly_report()
