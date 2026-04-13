#!/usr/bin/env python3
"""
金融知识图谱生成
- 构建 股票 - 新闻 - 情感 关联图谱
- 使用 NetworkX 进行图分析
- 输出图谱数据供前端可视化
"""
import sys
import json
from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict
sys.path.insert(0, '/root/finance-dashboard/backend')

import networkx as nx
from industry_mapping import (
    INDUSTRY_MAP, STOCK_TO_INDUSTRY, 
    THEME_KEYWORDS, detect_theme, get_industry
)

class DecimalEncoder(json.JSONEncoder):
    """处理 Decimal 类型的 JSON 编码器"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

from db import get_db_connection
from vectorize_news import NewsVectorizer
import numpy as np

class FinancialKnowledgeGraph:
    """金融知识图谱"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.vectorizer = NewsVectorizer()
    
    def build_graph_from_db(self, days=7):
        """从数据库构建图谱"""
        print("\n🕸️  从数据库构建知识图谱...")
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # 获取最近的新闻数据
            cur.execute("""
                SELECT title, content, sentiment_label, related_symbols, sentiment_score, created_at
                FROM news
                WHERE created_at >= NOW() - INTERVAL '%s days'
                AND related_symbols IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 500
            """, (days,))
            
            news_items = cur.fetchall()
            
            # 获取股票数据
            cur.execute("""
                SELECT DISTINCT ON (symbol)
                    symbol, price, change_percent, volume, timestamp
                FROM market_data
                ORDER BY symbol, timestamp DESC
            """)
            
            stocks = cur.fetchall()
            
            cur.close()
        
        # 1. 添加行业节点
        print("   🏭 添加行业节点...")
        self._add_industry_nodes()
        
        # 2. 添加股票节点
        print(f"   📊 添加 {len(stocks)} 个股票节点...")
        for stock in stocks:
            symbol, price, change_pct, volume, timestamp = stock
            industry = get_industry(symbol)
            self.graph.add_node(
                f"stock:{symbol}",
                type='stock',
                symbol=symbol,
                price=price,
                change_percent=change_pct,
                volume=volume,
                industry=industry,
                label=f"{symbol}\n${price:.2f}\n{change_pct:+.1f}%"
            )
            # 添加股票→行业边
            if industry != '其他':
                self.graph.add_edge(
                    f"stock:{symbol}",
                    f"industry:{industry}",
                    relation='belongs_to',
                    weight=1.0
                )
        
        # 3. 添加新闻节点和关联边（含主题分析）
        print(f"   📰 添加 {len(news_items)} 条新闻节点...")
        news_count = 0
        theme_stats = defaultdict(int)
        
        for title, content, sentiment, symbols, score, created_at in news_items:
            if not symbols:
                continue
            
            # 主题检测
            themes = detect_theme(title, content or '')
            for theme in themes:
                theme_stats[theme] += 1
            
            news_id = f"news:{news_count}"
            self.graph.add_node(
                news_id,
                type='news',
                title=title[:100],
                sentiment=sentiment,
                score=score,
                date=created_at.strftime('%Y-%m-%d'),
                themes=list(themes.keys()),
                label=f"{sentiment}\n{title[:40]}..."
            )
            
            # 添加新闻与股票的关联边
            for symbol in symbols[:5]:
                if f"stock:{symbol}" in self.graph.nodes:
                    edge_weight = abs(score) if score else 0.5
                    self.graph.add_edge(
                        news_id,
                        f"stock:{symbol}",
                        relation='mentions',
                        weight=edge_weight,
                        sentiment=sentiment
                    )
            
            # 添加新闻→主题边
            for theme_name, theme_data in themes.items():
                theme_node_id = f"theme:{theme_name}"
                if theme_node_id not in self.graph.nodes:
                    self.graph.add_node(
                        theme_node_id,
                        type='theme',
                        name=self._get_theme_label(theme_name),
                        impact=theme_data.get('impact', ''),
                        label=self._get_theme_label(theme_name)
                    )
                
                self.graph.add_edge(
                    news_id,
                    theme_node_id,
                    relation='about',
                    weight=theme_data['score']
                )
            
            news_count += 1
        
        # 4. 添加股票共现边
        print("   🔗 添加股票共现关联...")
        self._add_stock_correlations(min_count=2)
        
        # 5. 添加主题→资产关联
        print("   🎯 添加主题 - 资产关联...")
        self._add_theme_asset_links()
        
        print(f"   ✅ 图谱构建完成：{self.graph.number_of_nodes()} 节点，{self.graph.number_of_edges()} 边")
        
        # 输出主题统计
        if theme_stats:
            print("\n   📊 主题分布:")
            for theme, count in sorted(theme_stats.items(), key=lambda x: -x[1])[:5]:
                print(f"      {self._get_theme_label(theme)}: {count} 条")
        
        return self.graph
    
    def _add_industry_nodes(self):
        """添加行业节点"""
        industry_colors = {
            '科技': '#8b5cf6',    # 紫色
            '加密货币': '#f59e0b', # 橙色
            '汽车': '#ef4444',    # 红色
            '电商': '#10b981',    # 绿色
            '金融': '#3b82f6',    # 蓝色
            '能源': '#f97316',    # 橙色
            '医药': '#ec4899',    # 粉色
            '消费': '#14b8a6'     # 青色
        }
        
        for industry in INDUSTRY_MAP.keys():
            self.graph.add_node(
                f"industry:{industry}",
                type='industry',
                name=f'{industry}板块',
                color=industry_colors.get(industry, '#6b7280'),
                stock_count=len(INDUSTRY_MAP.get(industry, [])),
                label=f'{industry}板块'
            )
    
    def _get_theme_label(self, theme_name):
        """获取主题的中文标签"""
        theme_labels = {
            'war_geopolitics': '⚔️ 战争/地缘政治',
            'ai_tech': '🤖 AI/人工智能',
            'oil_energy': '🛢️ 石油/能源',
            'gold_precious': '🥇 黄金/贵金属',
            'fed_rate': '🏦 美联储/利率',
            'ev_auto': '🚗 电动汽车'
        }
        return theme_labels.get(theme_name, theme_name)
    
    def _add_stock_correlations(self, min_count=2):
        """添加股票之间的共现关联"""
        # 统计股票共同出现在新闻中的次数
        stock_cooccurrence = {}
        
        for node in self.graph.nodes(data=True):
            if node[1].get('type') == 'news':
                # 获取这条新闻关联的所有股票
                news_edges = self.graph.edges(node[0], data=True)
                stocks = [edge[1] for edge in news_edges if edge[1].startswith('stock:')]
                
                # 两两统计共现
                for i, stock1 in enumerate(stocks):
                    for stock2 in stocks[i+1:]:
                        key = tuple(sorted([stock1, stock2]))
                        stock_cooccurrence[key] = stock_cooccurrence.get(key, 0) + 1
        
        # 添加共现边（至少共现 min_count 次）
        for (stock1, stock2), count in stock_cooccurrence.items():
            if count >= min_count:
                self.graph.add_edge(
                    stock1,
                    stock2,
                    relation='co_occurrence',
                    weight=min(count / 5.0, 3.0),  # 归一化，最大 3.0
                    co_count=count,
                    label=f'共同提及 {count} 次'
                )
    
    def _count_mentions(self, symbol):
        """统计股票被新闻提及的次数"""
        count = 0
        for node in self.graph.nodes(data=True):
            if node[1].get('type') == 'news':
                edges = self.graph.edges(node[0], data=True)
                for edge in edges:
                    if edge[1] == f"stock:{symbol}":
                        count += 1
                        break
        return count
    
    def _add_theme_asset_links(self):
        """添加主题与相关资产的关联"""
        # 为每个主题添加相关的资产节点（即使新闻中没有直接提及）
        for theme_name, theme_data in THEME_KEYWORDS.items():
            theme_node_id = f"theme:{theme_name}"
            
            if theme_node_id not in self.graph.nodes:
                continue
            
            # 添加主题相关的资产
            for asset in theme_data.get('related_assets', []):
                asset_node_id = f"asset:{asset}"
                
                if asset_node_id not in self.graph.nodes:
                    # 判断资产类型
                    if asset.endswith('-USD'):
                        asset_type = 'crypto'
                        label = asset.replace('-USD', '')
                    elif asset in ['GLD', 'GC=F']:
                        asset_type = 'gold'
                        label = '黄金'
                    elif asset in ['XOM', 'CVX', 'COP', 'SLB', 'USO']:
                        asset_type = 'oil'
                        label = asset
                    else:
                        asset_type = 'stock'
                        label = asset
                    
                    self.graph.add_node(
                        asset_node_id,
                        type='related_asset',
                        asset_type=asset_type,
                        symbol=asset,
                        label=f"{label}\n({asset_type})"
                    )
                
                # 添加主题→资产边
                if not self.graph.has_edge(theme_node_id, asset_node_id):
                    self.graph.add_edge(
                        theme_node_id,
                        asset_node_id,
                        relation='related_to',
                        weight=1.0,
                        label='相关资产'
                    )
    
    def analyze_graph(self):
        """图谱分析"""
        print("\n🔍 图谱分析...")
        
        if self.graph.number_of_nodes() == 0:
            print("   ⚠️ 图谱为空")
            return {}
        
        # 基础统计
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'stock_nodes': sum(1 for n, d in self.graph.nodes(data=True) if d.get('type') == 'stock'),
            'news_nodes': sum(1 for n, d in self.graph.nodes(data=True) if d.get('type') == 'news'),
        }
        
        # 中心性分析（找出最关键的股票）
        if self.graph.number_of_edges() > 0:
            try:
                # 入度中心性（被最多新闻提及）
                in_degree = dict(self.graph.in_degree())
                top_mentioned = sorted(
                    [(n, d) for n, d in in_degree.items() if n.startswith('stock:')],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                stats['top_mentioned_stocks'] = [
                    {'symbol': n.replace('stock:', ''), 'mentions': d}
                    for n, d in top_mentioned
                ]
            except Exception as e:
                print(f"   ⚠️ 中心性分析失败：{e}")
        
        # 社群检测（找出关联紧密的股票群）
        try:
            # 转换为无向图进行社群检测
            undirected = self.graph.to_undirected()
            if undirected.number_of_nodes() > 0:
                from networkx.algorithms import community
                communities = community.greedy_modularity_communities(undirected)
                
                # 只保留包含股票的社群
                stock_communities = []
                for i, comm in enumerate(communities[:5]):  # 最多 5 个社群
                    stocks_in_comm = [n.replace('stock:', '') for n in comm if n.startswith('stock:')]
                    if len(stocks_in_comm) >= 2:
                        stock_communities.append({
                            'community_id': i,
                            'stocks': stocks_in_comm,
                            'size': len(stocks_in_comm)
                        })
                
                stats['communities'] = stock_communities
        except Exception as e:
            print(f"   ⚠️ 社群检测失败：{e}")
        
        print(f"   ✅ 分析完成")
        return stats
    
    def export_for_frontend(self, output_path='/root/finance-dashboard/backend/graph_data.json'):
        """导出图谱数据供前端使用"""
        print(f"\n💾 导出图谱数据到 {output_path}...")
        
        nodes = []
        links = []
        
        # 导出节点
        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get('type', 'unknown')
            
            # 设置节点颜色和大小
            if node_type == 'stock':
                color = '#22c55e' if data.get('change_percent', 0) >= 0 else '#ef4444'
                # 基于提及次数优化大小
                mention_count = self._count_mentions(data.get('symbol', ''))
                size = 15 + mention_count * 3 + abs(data.get('change_percent', 0)) * 2
            elif node_type == 'industry':
                color = data.get('color', '#8b5cf6')
                size = 30 + (data.get('stock_count', 0) or 0) * 3
            elif node_type == 'theme':
                color = '#ec4899'
                size = 25
            elif node_type == 'related_asset':
                asset_type = data.get('asset_type', 'other')
                color_map = {
                    'crypto': '#f59e0b',
                    'gold': '#fbbf24',
                    'oil': '#f97316',
                    'stock': '#667eea'
                }
                color = color_map.get(asset_type, '#6b7280')
                size = 20
            else:  # news
                sentiment = data.get('sentiment', 'neutral')
                if sentiment == 'positive':
                    color = '#3b82f6'
                elif sentiment == 'negative':
                    color = '#f97316'
                else:
                    color = '#6b7280'
                size = 12
            
            nodes.append({
                'id': node_id,
                'type': node_type,
                'label': data.get('label', node_id),
                'color': color,
                'size': size,
                'data': {k: v for k, v in data.items() if k not in ['label']}
            })
        
        # 导出边
        for source, target, data in self.graph.edges(data=True):
            relation = data.get('relation', 'related')
            weight = data.get('weight', 1.0)
            
            links.append({
                'source': source,
                'target': target,
                'relation': relation,
                'weight': weight,
                'label': data.get('label', relation)
            })
        
        # 导出分析结果
        stats = self.analyze_graph()
        
        output_data = {
            'generated_at': datetime.now().isoformat(),
            'stats': stats,
            'nodes': nodes[:200],  # 限制节点数量
            'links': links[:500],  # 限制边数量
            'full_stats': stats
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
        
        print(f"   ✅ 已导出 {len(nodes)} 节点，{len(links)} 边")
        return output_data

def generate_knowledge_graph(days=7):
    """主函数：生成知识图谱"""
    print(f"\n🕸️  开始生成金融知识图谱 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    graph = FinancialKnowledgeGraph()
    
    # 构建图谱
    graph.build_graph_from_db(days=days)
    
    # 分析图谱
    stats = graph.analyze_graph()
    
    # 导出数据
    graph.export_for_frontend()
    
    print("\n" + "=" * 60)
    print(f"✅ 知识图谱生成完成！")
    print(f"📊 统计：{stats.get('total_nodes', 0)} 节点，{stats.get('total_edges', 0)} 边")
    
    if stats.get('top_mentioned_stocks'):
        print("🔝 最热股票:")
        for stock in stats['top_mentioned_stocks'][:3]:
            print(f"   - {stock['symbol']}: {stock['mentions']} 次提及")
    
    if stats.get('communities'):
        print(f"👥 发现 {len(stats['communities'])} 个股票社群")
    
    print("=" * 60)

if __name__ == "__main__":
    generate_knowledge_graph(days=7)
