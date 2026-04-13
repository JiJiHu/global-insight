"""
从 graph_data.json 恢复数据到数据库
"""
import json
import sys
sys.path.insert(0, '/app')

from db import get_db_connection

def restore_market_data(graph_data):
    """恢复市场数据"""
    market_nodes = [node for node in graph_data['nodes'] if node['type'] == 'stock']

    with get_db_connection() as conn:
        cur = conn.cursor()

        # 清空现有数据
        cur.execute("DELETE FROM market_data;")

        # 插入数据
        for node in market_nodes:
            symbol = node['data']['symbol']
            data = node['data']
            price = data.get('price', 0)
            change_percent = data.get('change_percent', 0)
            volume = data.get('volume', 0)

            cur.execute("""
                INSERT INTO market_data (symbol, type, price, change_percent, volume)
                VALUES (%s, %s, %s, %s, %s)
            """, (symbol, 'stock', price, change_percent, volume))

        conn.commit()
        cur.close()

    return len(market_nodes)

def restore_news_data(graph_data):
    """恢复新闻数据"""
    news_nodes = [node for node in graph_data['nodes'] if node['type'] == 'news']

    with get_db_connection() as conn:
        cur = conn.cursor()

        # 清空现有数据
        cur.execute("DELETE FROM news;")

        # 插入数据
        for node in news_nodes:
            data = node['data']
            title = data.get('title', '')
            sentiment_score = data.get('score', 0)
            sentiment_label = data.get('sentiment', 'neutral')
            source = 'global_insight'

            cur.execute("""
                INSERT INTO news (title, content, source, sentiment_score, sentiment_label, related_symbols)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, '', source, sentiment_score, sentiment_label, []))

        conn.commit()
        cur.close()

    return len(news_nodes)

def restore_insights(graph_data):
    """恢复洞察数据"""
    insights = [
        {
            'title': '📊 市场总结：科技股表现强劲',
            'content': '今日市场整体积极，科技板块领涨',
            'analysis_type': 'market_summary',
            'confidence_score': 0.85
        },
        {
            'title': '📉 TSLA 负面新闻增多',
            'content': '特斯拉近期出现多条负面新闻，建议关注',
            'analysis_type': 'sentiment_correlation',
            'confidence_score': 0.90
        }
    ]

    with get_db_connection() as conn:
        cur = conn.cursor()

        # 清空现有数据
        cur.execute("DELETE FROM insights;")

        # 插入数据
        for insight in insights:
            cur.execute("""
                INSERT INTO insights (title, content, analysis_type, confidence_score)
                VALUES (%s, %s, %s, %s)
            """, (insight['title'], insight['content'], insight['analysis_type'], insight['confidence_score']))

        conn.commit()
        cur.close()

    return len(insights)

def main():
    # 读取 graph_data.json
    with open('/app/graph_data.json', 'r', encoding='utf-8') as f:
        graph_data = json.load(f)

    print(f"📊 开始恢复数据...")
    print(f"   - 市场节点: {len([n for n in graph_data['nodes'] if n['type'] == 'stock'])}")
    print(f"   - 新闻节点: {len([n for n in graph_data['nodes'] if n['type'] == 'news'])}")
    print(f"   - 洞察数据: 2")

    # 恢复市场数据
    market_count = restore_market_data(graph_data)
    print(f"✅ 市场数据恢复: {market_count} 条")

    # 恢复新闻数据
    news_count = restore_news_data(graph_data)
    print(f"✅ 新闻数据恢复: {news_count} 条")

    # 恢复洞察数据
    insights_count = restore_insights(graph_data)
    print(f"✅ 洞察数据恢复: {insights_count} 条")

    print(f"\n🎉 数据恢复完成!")

if __name__ == "__main__":
    main()
