#!/usr/bin/env python3
"""
AI 洞察生成脚本
- 分析金融数据与新闻的关联
- 自动生成洞察报告
"""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, '/root/finance-dashboard/backend')

from vectorize_news import NewsVectorizer
from db import get_db_connection
import numpy as np

def analyze_price_news_correlation():
    """分析价格波动与新闻的关联 (基于规则 + 统计)"""
    print("\n🧠 分析价格 - 新闻关联性...")
    
    insights = []
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取有负面新闻的股票
        cur.execute("""
            WITH negative_news AS (
                SELECT 
                    UNNEST(related_symbols) as symbol,
                    COUNT(*) as negative_count,
                    AVG(sentiment_score) as avg_sentiment
                FROM news
                WHERE sentiment_label = 'negative'
                  AND related_symbols IS NOT NULL
                GROUP BY UNNEST(related_symbols)
            ),
            latest_prices AS (
                SELECT DISTINCT ON (symbol)
                    symbol, price, change_percent, timestamp
                FROM market_data
                ORDER BY symbol, timestamp DESC
            )
            SELECT 
                nn.symbol,
                nn.negative_count,
                nn.avg_sentiment,
                lp.price,
                lp.change_percent
            FROM negative_news nn
            JOIN latest_prices lp ON nn.symbol = lp.symbol
            WHERE nn.negative_count >= 2
            ORDER BY nn.negative_count DESC
            LIMIT 5
        """)
        
        negative_results = cur.fetchall()
        
        for row in negative_results:
            symbol, negative_count, avg_sentiment, price, change_percent = row
            
            # 生成洞察
            if change_percent and change_percent < -2:
                insight = {
                    'title': f'{symbol} 负面新闻增多，股价下跌 {abs(change_percent):.1f}%',
                    'content': f'{symbol} 近期出现 {negative_count} 条负面新闻，平均情感得分 {avg_sentiment:.2f}。'
                              f'当前股价 ${price:.2f}，今日下跌 {abs(change_percent):.1f}%。'
                              f'建议关注后续新闻动向和公司公告。',
                    'analysis_type': 'sentiment_correlation',
                    'confidence_score': min(0.5 + (negative_count * 0.1), 0.95)
                }
                insights.append(insight)
        
        # 获取有正面新闻的股票
        cur.execute("""
            WITH positive_news AS (
                SELECT 
                    UNNEST(related_symbols) as symbol,
                    COUNT(*) as positive_count,
                    AVG(sentiment_score) as avg_sentiment
                FROM news
                WHERE sentiment_label = 'positive'
                  AND related_symbols IS NOT NULL
                GROUP BY UNNEST(related_symbols)
            ),
            latest_prices AS (
                SELECT DISTINCT ON (symbol)
                    symbol, price, change_percent, timestamp
                FROM market_data
                ORDER BY symbol, timestamp DESC
            )
            SELECT 
                pn.symbol,
                pn.positive_count,
                pn.avg_sentiment,
                lp.price,
                lp.change_percent
            FROM positive_news pn
            JOIN latest_prices lp ON pn.symbol = lp.symbol
            WHERE pn.positive_count >= 2
            ORDER BY pn.positive_count DESC
            LIMIT 5
        """)
        
        positive_results = cur.fetchall()
        
        for row in positive_results:
            symbol, positive_count, avg_sentiment, price, change_percent = row
            
            # 生成洞察
            if change_percent and change_percent > 2:
                insight = {
                    'title': f'{symbol} 利好新闻推动，股价上涨 {change_percent:.1f}%',
                    'content': f'{symbol} 近期获得 {positive_count} 条正面新闻，平均情感得分 {avg_sentiment:.2f}。'
                              f'当前股价 ${price:.2f}，今日上涨 {change_percent:.1f}%。'
                              f'市场情绪积极，可持续关注。',
                    'analysis_type': 'sentiment_correlation',
                    'confidence_score': min(0.5 + (positive_count * 0.1), 0.95)
                }
                insights.append(insight)
        
        cur.close()
    
    print(f"   ✅ 生成 {len(insights)} 条关联分析洞察")
    return insights

def generate_market_summary():
    """生成市场总结"""
    print("\n📊 生成市场总结...")
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取整体市场情况
        cur.execute("""
            SELECT 
                COUNT(DISTINCT symbol) as total_symbols,
                AVG(change_percent) as avg_change,
                MAX(change_percent) as max_gain,
                MIN(change_percent) as max_loss
            FROM (
                SELECT DISTINCT ON (symbol)
                    symbol, change_percent
                FROM market_data
                ORDER BY symbol, timestamp DESC
            ) latest
        """)
        
        result = cur.fetchone()
        total_symbols, avg_change, max_gain, max_loss = result
        
        # 判断市场情绪
        if avg_change > 1:
            market_sentiment = "积极"
            sentiment_emoji = "📈"
        elif avg_change < -1:
            market_sentiment = "消极"
            sentiment_emoji = "📉"
        else:
            market_sentiment = "震荡"
            sentiment_emoji = "➡️"
        
        insight = {
            'title': f'{sentiment_emoji} 市场总结：{total_symbols} 只股票平均涨跌 {avg_change:.2f}%',
            'content': f'今日市场整体{market_sentiment}。{total_symbols} 只监控股票中，'
                      f'平均涨跌幅 {avg_change:.2f}%，表现最好的上涨 {max_gain:.2f}%，'
                      f'表现最差的下跌 {abs(max_loss):.2f}%。'
                      f'建议关注市场动向，合理配置资产。',
            'analysis_type': 'market_summary',
            'confidence_score': 0.85
        }
        
        cur.close()
    
    print(f"   ✅ 生成市场总结")
    return [insight]

def generate_top_news_insight():
    """生成头条新闻洞察"""
    print("\n📰 分析头条新闻...")
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取最新的重要新闻
        cur.execute("""
            SELECT title, sentiment_label, related_symbols, created_at
            FROM news
            WHERE source IN ('finnhub-top', 'china-top', 'tech-top', 'crypto-top')
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        news_results = cur.fetchall()
        
        insights = []
        for row in news_results:
            title, sentiment, symbols, created_at = row
            
            if symbols:
                symbol_str = ', '.join(symbols[:3])
                insight = {
                    'title': f'🔔 重要新闻：{title[:50]}...',
                    'content': f'涉及标的：{symbol_str}。情感倾向：{sentiment}。'
                              f'建议关注相关新闻对股价的影响。',
                    'analysis_type': 'news_alert',
                    'confidence_score': 0.75
                }
                insights.append(insight)
        
        cur.close()
    
    print(f"   ✅ 生成 {len(insights)} 条新闻洞察")
    return insights

def save_insights(insights):
    """保存洞察到数据库"""
    if not insights:
        print("⚠️ 没有洞察需要保存")
        return
    
    print(f"\n💾 保存 {len(insights)} 条洞察到数据库...")
    
    vectorizer = NewsVectorizer()
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        for insight in insights:
            # 生成向量化嵌入
            full_text = f"{insight['title']} {insight['content']}"
            embedding = vectorizer.generate_embedding(full_text)
            
            # 插入数据库
            cur.execute("""
                INSERT INTO insights 
                (title, content, analysis_type, confidence_score, embedding)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                insight['title'],
                insight['content'],
                insight['analysis_type'],
                insight['confidence_score'],
                embedding
            ))
        
        conn.commit()
        cur.close()
    
    print(f"✅ 已保存 {len(insights)} 条洞察")

def generate_all_insights():
    """主函数：生成所有洞察"""
    print(f"\n🧠 开始生成 AI 洞察 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 价格 - 新闻关联分析
    correlation_insights = analyze_price_news_correlation()
    
    # 2. 市场总结
    summary_insight = generate_market_summary()
    
    # 3. 头条新闻洞察
    news_insights = generate_top_news_insight()
    
    # 合并所有洞察
    all_insights = correlation_insights + summary_insight + news_insights
    
    # 保存到数据库
    save_insights(all_insights)
    
    print("\n" + "=" * 60)
    print(f"✅ AI 洞察生成完成！共 {len(all_insights)} 条")
    print("=" * 60)

if __name__ == "__main__":
    generate_all_insights()
