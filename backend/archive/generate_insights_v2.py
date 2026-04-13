#!/usr/bin/env python3
"""
AI 洞察生成脚本 v2
- 增加数据源维度（RSS 新闻、社交媒体）
- 添加去重逻辑
- 生成更多类型的洞察
"""

from datetime import datetime, timedelta
from db import get_db_connection
import hashlib

def dedup_insights(insights_list):
    """基于标题去重，保留最新"""
    seen = {}
    
    for insight in insights_list:
        title_hash = hashlib.md5(insight['title'].encode()).hexdigest()
        # 保留最新的（如果有重复）
        if title_hash not in seen or insight['created_at'] > seen[title_hash]['created_at']:
            seen[title_hash] = insight
    
    return list(seen.values())

def generate_market_summary():
    """生成市场总结"""
    insights = []
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取所有股票的最新数据
        cur.execute("""
            SELECT DISTINCT ON (symbol) symbol, price, change_percent, type
            FROM market_data
            WHERE type = 'stock'
            ORDER BY symbol, timestamp DESC
        """)
        stocks = cur.fetchall()
        
        if stocks:
            count = len(stocks)
            avg_change = sum(s[2] for s in stocks if s[2]) / count
            max_gain = max(stocks, key=lambda x: x[2] if x[2] else 0)
            max_loss = min(stocks, key=lambda x: x[2] if x[2] else 0)
            
            # 判断市场情绪
            if avg_change > 1:
                sentiment = "强势上涨"
            elif avg_change > 0:
                sentiment = "震荡上行"
            elif avg_change > -1:
                sentiment = "震荡整理"
            else:
                sentiment = "回调下跌"
            
            insight = {
                'title': f'📊 市场总结：{count} 只股票平均涨跌 {avg_change:.2f}%',
                'content': f'今日市场整体{sentiment}。{count} 只监控股票中，平均涨跌幅 {avg_change:.2f}%，表现最好的{max_gain[0]}上涨{max_gain[2]:.2f}%，表现最差的{max_loss[0]}下跌{max_loss[2]:.2f}%。建议关注市场动向，合理配置资产。',
                'confidence': 0.9,
                'category': 'market_summary',
                'source': 'Global Insight',
                'created_at': datetime.now()
            }
            insights.append(insight)
    
    return insights

def generate_news_alerts():
    """生成重要新闻提醒"""
    insights = []
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取最新的负面新闻（影响较大的）
        cur.execute("""
            SELECT title, source, sentiment_label, url, created_at
            FROM news
            WHERE sentiment_label = 'negative'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        negative_news = cur.fetchall()
        
        for news in negative_news:
            title, source, sentiment, url, created_at = news
            
            # 提取关键词
            keywords = []
            if 'war' in title.lower() or 'conflict' in title.lower():
                keywords.append('地缘政治')
            if 'fed' in title.lower() or 'interest' in title.lower():
                keywords.append('货币政策')
            if 'earn' in title.lower() or 'profit' in title.lower():
                keywords.append('财报')
            
            keyword_str = '、'.join(keywords) if keywords else '市场动态'
            
            insight = {
                'title': f'🔔 重要新闻：{title[:50]}...',
                'content': f'来源：{source}。情感倾向：{sentiment}。关键词：{keyword_str}。建议关注相关新闻对股价的影响。[查看详情]({url})',
                'confidence': 0.75,
                'category': 'news_alert',
                'source': source,
                'url': url,
                'created_at': created_at
            }
            insights.append(insight)
        
        # 获取正面新闻
        cur.execute("""
            SELECT title, source, sentiment_label, url, created_at
            FROM news
            WHERE sentiment_label = 'positive'
            ORDER BY created_at DESC
            LIMIT 3
        """)
        positive_news = cur.fetchall()
        
        for news in positive_news:
            title, source, sentiment, url, created_at = news
            
            insight = {
                'title': f'✅ 利好消息：{title[:50]}...',
                'content': f'来源：{source}。情感倾向：{sentiment}。可能带来投资机会。[查看详情]({url})',
                'confidence': 0.7,
                'category': 'opportunity',
                'source': source,
                'url': url,
                'created_at': created_at
            }
            insights.append(insight)
    
    return insights

def generate_sector_analysis():
    """生成行业分析"""
    insights = []
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 统计各类型资产表现
        cur.execute("""
            SELECT type, AVG(change_percent) as avg_change, COUNT(*) as count
            FROM market_data
            WHERE change_percent IS NOT NULL
            GROUP BY type
            ORDER BY avg_change DESC
        """)
        sectors = cur.fetchall()
        
        if sectors:
            best_sector = sectors[0]
            worst_sector = sectors[-1]
            
            insight = {
                'title': f'📈 行业分析：{best_sector[0]} 板块领涨',
                'content': f'{best_sector[0]} 板块平均上涨 {best_sector[1]:.2f}%（{best_sector[2]} 只标的），表现最佳。{worst_sector[0]} 板块平均{worst_sector[1]:.2f}%（{worst_sector[2]} 只标的），表现落后。建议关注强势板块的投资机会。',
                'confidence': 0.8,
                'category': 'sector_analysis',
                'source': 'Global Insight',
                'created_at': datetime.now()
            }
            insights.append(insight)
    
    return insights

def generate_crypto_insights():
    """生成加密货币洞察"""
    insights = []
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT ON (symbol) symbol, price, change_percent
            FROM market_data
            WHERE type = 'crypto'
            ORDER BY symbol, timestamp DESC
        """)
        cryptos = cur.fetchall()
        
        if cryptos:
            btc = next((c for c in cryptos if c[0] == 'BTC'), None)
            eth = next((c for c in cryptos if c[0] == 'ETH'), None)
            
            if btc:
                btc_sentiment = "强势" if btc[2] > 2 else "震荡" if btc[2] > -2 else "弱势"
                insight = {
                    'title': f'₿ 加密货币：BTC {btc_sentiment}',
                    'content': f'比特币价格 ${btc[1]:,.2f}，24 小时涨跌 {btc[2]:.2f}%。{"市场情绪乐观，建议关注" if btc[2] > 0 else "注意风险控制"}。',
                    'confidence': 0.75,
                    'category': 'crypto',
                    'source': 'CoinGecko',
                    'created_at': datetime.now()
                }
                insights.append(insight)
    
    return insights

def save_insights(insights):
    """保存洞察到数据库"""
    # 先删除旧的洞察（保留最近 10 条）
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        for insight in insights:
            try:
                # 简化插入，不保存 URL 到数组
                cur.execute("""
                    INSERT INTO insights 
                    (title, content, confidence_score, analysis_type, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    insight['title'],
                    insight['content'],
                    insight['confidence'],
                    insight['category'],
                    insight['created_at']
                ))
            except Exception as e:
                print(f"⚠️ 保存失败：{e}")
        
        conn.commit()
        cur.close()

def generate_all():
    """生成所有洞察"""
    print("\n🧠 开始生成 AI 洞察...")
    
    all_insights = []
    
    # 市场总结
    market_summary = generate_market_summary()
    all_insights.extend(market_summary)
    print(f"  ✅ 市场总结：{len(market_summary)} 条")
    
    # 新闻提醒
    news_alerts = generate_news_alerts()
    all_insights.extend(news_alerts)
    print(f"  ✅ 新闻提醒：{len(news_alerts)} 条")
    
    # 行业分析
    sector_analysis = generate_sector_analysis()
    all_insights.extend(sector_analysis)
    print(f"  ✅ 行业分析：{len(sector_analysis)} 条")
    
    # 加密货币
    crypto_insights = generate_crypto_insights()
    all_insights.extend(crypto_insights)
    print(f"  ✅ 加密货币：{len(crypto_insights)} 条")
    
    # 去重
    unique_insights = dedup_insights(all_insights)
    print(f"\n✅ 去重后：{len(unique_insights)} 条洞察")
    
    # 保存
    save_insights(unique_insights)
    print(f"💾 已保存到数据库")
    
    return unique_insights

if __name__ == "__main__":
    generate_all()
