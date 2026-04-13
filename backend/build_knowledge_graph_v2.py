#!/usr/bin/env python3
"""
知识图谱 v2 - 添加关系边
关系类型：
1. 股票 → 行业（belongs_to）
2. 股票 → 竞争对手（competes_with）
3. 新闻 → 涉及股票（mentions）
4. 新闻 → 来源（from_source）
5. 股票 → 新闻（related_news）
6. 行业 → 主题（related_theme）
"""

from db import get_db_connection
from datetime import datetime, timedelta
import json

# 行业映射
INDUSTRY_MAP = {
    '科技': ['AAPL', 'MSFT', 'NVDA', 'AMD', 'GOOGL', 'META'],
    '消费': ['AMZN', 'TSLA', 'NKE', 'MCD', 'SBUX'],
    '金融': ['JPM', 'BAC', 'GS', 'MS'],
    '医药': ['JNJ', 'PFE', 'MRNA', 'ABBV'],
    '能源': ['XOM', 'CVX', 'COP'],
    '通信': ['T', 'VZ', 'TMUS'],
}

# 竞争对手关系
COMPETITOR_MAP = {
    'AAPL': ['MSFT', 'GOOGL', 'AMZN'],  # 苹果 vs 微软/谷歌/亚马逊
    'MSFT': ['AAPL', 'GOOGL', 'AMZN'],  # 微软 vs 苹果/谷歌/亚马逊
    'GOOGL': ['AAPL', 'MSFT', 'META'],  # 谷歌 vs 苹果/微软/Meta
    'AMZN': ['AAPL', 'MSFT', 'GOOGL'],  # 亚马逊 vs 苹果/微软/谷歌
    'NVDA': ['AMD', 'INTC'],  # 英伟达 vs AMD/英特尔
    'AMD': ['NVDA', 'INTC'],  # AMD vs 英伟达/英特尔
    'META': ['GOOGL', 'SNAP'],  # Meta vs 谷歌/Snap
    'TSLA': ['NKE', 'F', 'GM'],  # 特斯拉 vs 耐克/福特/通用（跨行业竞争）
}

# 主题映射
THEME_MAP = {
    '人工智能': ['NVDA', 'MSFT', 'GOOGL', 'META', 'AMD'],
    '电动车': ['TSLA', 'NIO', 'XPEV'],
    '云计算': ['AMZN', 'MSFT', 'GOOGL'],
    '社交媒体': ['META', 'GOOGL', 'SNAP'],
    '半导体': ['NVDA', 'AMD', 'INTC', 'TSM'],
    '金融科技': ['PYPL', 'SQ', 'V', 'MA'],
}

def build_graph():
    """构建知识图谱"""
    print("\n🕸️ 开始构建知识图谱...")
    
    nodes = []
    links = []
    node_ids = set()
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 1. 获取股票数据
        cur.execute("""
            SELECT DISTINCT ON (symbol) symbol, price, change_percent, type
            FROM market_data
            ORDER BY symbol, timestamp DESC
        """)
        stocks = cur.fetchall()
        
        # 2. 获取新闻数据
        cur.execute("""
            SELECT id, title, source, sentiment_label, url, created_at
            FROM news
            ORDER BY created_at DESC
            LIMIT 100
        """)
        news_items = cur.fetchall()
        
        cur.close()
    
    # ========== 添加节点 ==========
    
    # 1. 股票节点
    print(f"   📊 添加 {len(stocks)} 个股票节点...")
    for stock in stocks:
        symbol, price, change, mtype = stock
        node_id = f"stock_{symbol}"
        
        if node_id not in node_ids:
            # 确定行业
            industry = '未知'
            for ind, symbols in INDUSTRY_MAP.items():
                if symbol in symbols:
                    industry = ind
                    break
            
            nodes.append({
                'id': node_id,
                'name': symbol,
                'type': 'stock',
                'category': industry,
                'symbol': symbol,
                'price': float(price) if price else 0,
                'change': float(change) if change else 0,
                'market_type': mtype or 'stock',
                'value': 30  # 节点大小
            })
            node_ids.add(node_id)
    
    # 2. 行业节点
    print(f"   🏭 添加行业节点...")
    industries_added = set()
    for industry, symbols in INDUSTRY_MAP.items():
        if industry not in industries_added:
            # 检查是否有股票属于该行业
            has_stocks = any(s[0] in symbols for s in stocks)
            if has_stocks:
                nodes.append({
                    'id': f"industry_{industry}",
                    'name': f'{industry}行业',
                    'type': 'industry',
                    'category': industry,
                    'stock_count': len(symbols),
                    'value': 50  # 行业节点更大
                })
                node_ids.add(f"industry_{industry}")
                industries_added.add(industry)
    
    # 3. 主题节点
    print(f"   🎯 添加主题节点...")
    for theme, symbols in THEME_MAP.items():
        has_stocks = any(s[0] in symbols for s in stocks)
        if has_stocks:
            nodes.append({
                'id': f"theme_{theme}",
                'name': theme,
                'type': 'theme',
                'category': theme,
                'related_stocks': len(symbols),
                'value': 40
            })
            node_ids.add(f"theme_{theme}")
    
    # 4. 新闻来源节点
    print(f"   📰 添加新闻来源节点...")
    sources = set(n[2] for n in news_items if n[2])
    for source in sources:
        source_id = f"source_{source}"
        if source_id not in node_ids:
            nodes.append({
                'id': source_id,
                'name': source,
                'type': 'source',
                'category': 'media',
                'value': 25
            })
            node_ids.add(source_id)
    
    # ========== 添加关系边 ==========
    
    # 1. 股票 → 行业（belongs_to）
    print("   🔗 添加股票 - 行业关系...")
    link_count = 0
    for stock in stocks:
        symbol = stock[0]
        for industry, symbols in INDUSTRY_MAP.items():
            if symbol in symbols:
                links.append({
                    'source': f"stock_{symbol}",
                    'target': f"industry_{industry}",
                    'type': 'belongs_to',
                    'label': '属于',
                    'value': 2
                })
                link_count += 1
                break
    print(f"      添加 {link_count} 条属于关系")
    
    # 2. 股票 → 竞争对手（competes_with）
    print("   🔗 添加竞争对手关系...")
    link_count = 0
    added_competitors = set()
    for symbol, competitors in COMPETITOR_MAP.items():
        for competitor in competitors:
            # 避免重复（A→B 和 B→A 只添加一次）
            pair = tuple(sorted([symbol, competitor]))
            if pair not in added_competitors:
                # 检查两个股票都存在
                stock_symbols = [s[0] for s in stocks]
                if symbol in stock_symbols and competitor in stock_symbols:
                    links.append({
                        'source': f"stock_{symbol}",
                        'target': f"stock_{competitor}",
                        'type': 'competes_with',
                        'label': '竞争',
                        'value': 3,
                        'lineStyle': {'color': '#ef4444', 'width': 2, 'type': 'dashed'}
                    })
                    added_competitors.add(pair)
                    link_count += 1
    print(f"      添加 {link_count} 条竞争关系")
    
    # 3. 股票 → 主题（related_theme）
    print("   🔗 添加股票 - 主题关系...")
    link_count = 0
    for theme, symbols in THEME_MAP.items():
        for symbol in symbols:
            stock_symbols = [s[0] for s in stocks]
            if symbol in stock_symbols:
                links.append({
                    'source': f"stock_{symbol}",
                    'target': f"theme_{theme}",
                    'type': 'related_theme',
                    'label': '相关',
                    'value': 2
                })
                link_count += 1
    print(f"      添加 {link_count} 条主题关系")
    
    # 4. 新闻 → 涉及股票（mentions）- 简化版，随机关联
    print("   🔗 添加新闻 - 股票关系...")
    link_count = 0
    stock_symbols = [s[0] for s in stocks]
    for news in news_items[:50]:  # 只处理前 50 条新闻
        news_id, title, source, sentiment, url, created_at = news
        
        # 简单关联：根据新闻 ID 哈希关联到股票
        news_hash = hash(news_id) % len(stock_symbols)
        related_symbol = stock_symbols[news_hash]
        
        links.append({
            'source': f"news_{news_id}",
            'target': f"stock_{related_symbol}",
            'type': 'mentions',
            'label': '提及',
            'value': 1
        })
        link_count += 1
        
        # 新闻 → 来源
        if source:
            links.append({
                'source': f"news_{news_id}",
                'target': f"source_{source}",
                'type': 'from_source',
                'label': '来自',
                'value': 1
            })
            link_count += 1
    print(f"      添加 {link_count} 条新闻关系")
    
    # ========== 输出结果 ==========
    print(f"\n✅ 知识图谱构建完成！")
    print(f"   节点数：{len(nodes)}")
    print(f"   边数：{len(links)}")
    
    return {
        'nodes': nodes,
        'links': links
    }

def save_to_file(graph_data, filepath='/app/graph_data.json'):
    """保存图谱数据到文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存到 {filepath}")
    
    # 同时保存到宿主机（通过挂载卷）
    try:
        with open('/root/finance-dashboard/backend/graph_data.json', 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到宿主机")
    except:
        pass

if __name__ == "__main__":
    graph_data = build_graph()
    save_to_file(graph_data)
    
    # 打印统计
    print("\n📊 图谱统计:")
    node_types = {}
    for n in graph_data['nodes']:
        t = n.get('type', 'unknown')
        node_types[t] = node_types.get(t, 0) + 1
    
    link_types = {}
    for l in graph_data['links']:
        t = l.get('type', 'unknown')
        link_types[t] = link_types.get(t, 0) + 1
    
    print("节点类型:")
    for t, c in node_types.items():
        print(f"  {t}: {c} 个")
    
    print("\n关系类型:")
    for t, c in link_types.items():
        print(f"  {t}: {c} 条")
