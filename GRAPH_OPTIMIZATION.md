# 🕸️ 知识图谱优化方案

**分析时间**: 2026-03-07 21:00  
**当前状态**: 基础功能正常，有优化空间

---

## 📊 当前图谱状态

### 基础数据
- **节点数**: 81 个 (股票 10 + 新闻 71)
- **边数**: 49 条
- **边的类型**: 仅 `mentions` (新闻→股票)
- **时间范围**: 最近 7 天

### 数据分布
```
新闻情感:
  ❌ negative: 51 条 (72%)
  ✅ positive: 20 条 (28%)

热门股票:
  🥇 GOOGL: 19 次提及
  🥈 BTC-USD: 11 次提及
  🥉 META: 10 次提及
```

### 问题诊断

| 问题 | 严重程度 | 影响 |
|------|---------|------|
| ❌ 边类型单一 | 🟡 中 | 关系不够丰富 |
| ❌ 无社群结构 | 🟡 中 | 缺少股票关联分析 |
| ❌ 时间维度缺失 | 🟢 低 | 无法看趋势 |
| ❌ 节点大小差异小 | 🟢 低 | 视觉效果不明显 |
| ❌ 无行业分类 | 🟡 中 | 缺少行业维度 |

---

## 🎯 优化建议（按优先级）

### 🔴 P0 - 核心优化

#### 1. 增加边的类型

**当前**: 只有 `mentions` (新闻提及股票)

**建议新增**:
```python
# 股票 → 股票 共现关系
co_occurrence: 共同被新闻提及 ≥3 次

# 股票 → 股票 行业关系
same_industry: 同一行业板块

# 股票 → 股票 价格关联
price_correlated: 价格走势相关系数 > 0.7

# 新闻 → 新闻 相似关系
similar_topic: 主题相似度 > 0.8
```

**实现代码**:
```python
# 添加股票共现边（至少共现 3 次）
def add_co_occurrence_edges(self, min_count=3):
    """添加股票共同提及关系"""
    # ...统计共同出现在新闻中的股票对
    # 添加边：stock:AAPL --co_occurrence--> stock:GOOGL
```

**预期效果**:
- 边数量增加 50-100 条
- 图谱更丰富，发现隐藏关联

---

#### 2. 增强社群检测

**当前**: 未检测到明显社群

**问题**: 节点太少，边类型单一

**解决方案**:
```python
# 使用更宽松的社群检测算法
from networkx.algorithms import community

# 方法 1: Label Propagation (适合小图谱)
communities = community.label_propagation_communities(undirected)

# 方法 2: 基于行业手动分组
industry_groups = {
    '科技': ['AAPL', 'GOOGL', 'MSFT', 'META', 'NVDA', 'AMD'],
    '加密货币': ['BTC-USD', 'ETH-USD'],
    '汽车': ['TSLA'],
    '电商': ['AMZN']
}
```

**预期效果**:
- 检测出 2-4 个社群
- 前端可用不同颜色区分

---

#### 3. 添加行业/板块维度

**新增节点类型**:
```python
# 行业节点
self.graph.add_node(
    "industry:科技",
    type='industry',
    name='科技板块',
    color='#8b5cf6'
)

# 添加股票→行业边
self.graph.add_edge(
    "stock:AAPL",
    "industry:科技",
    relation='belongs_to',
    weight=1.0
)
```

**行业分类**:
| 行业 | 股票 |
|------|------|
| 🖥️ 科技 | AAPL, GOOGL, MSFT, META, NVDA, AMD |
| 🚗 汽车 | TSLA |
| 🛒 电商 | AMZN |
| ₿ 加密货币 | BTC-USD, ETH-USD |

**预期效果**:
- 增加 4-5 个行业节点
- 增加 10 条 belongs_to 边
- 更清晰的板块结构

---

### 🟡 P1 - 体验优化

#### 4. 时间维度分析

**新增功能**:
```python
# 按日期分组统计
def get_timeline_data(self, days=7):
    """获取时间线数据"""
    # 每天的节点数、边数
    # 每天的情感分布
    # 热门股票变化趋势
```

**前端展示**:
- 折线图：每天新闻数量
- 柱状图：每天情感分布
- 热力图：股票提及频率

---

#### 5. 增强视觉效果

**节点大小优化**:
```python
# 当前：大小差异不明显 (10-27)
# 优化：基于提及次数和涨跌幅

if node_type == 'stock':
    # 提及次数权重 + 涨跌幅权重
    mention_count = self._count_mentions(symbol)
    size = 15 + mention_count * 2 + abs(change_percent) * 3
    # 范围：15 - 60
```

**颜色优化**:
```python
# 股票节点：按行业分组
industry_colors = {
    '科技': '#8b5cf6',    # 紫色
    '汽车': '#ef4444',    # 红色
    '电商': '#10b981',    # 绿色
    '加密货币': '#f59e0b' # 橙色
}

# 新闻节点：按情感
sentiment_colors = {
    'positive': '#3b82f6',   # 蓝色
    'negative': '#ef4444',   # 红色
    'neutral': '#6b7280'     # 灰色
}
```

---

#### 6. 交互增强

**新增交互**:
```javascript
// 1. 点击节点高亮相邻节点
chart.on('click', (params) => {
    highlightAdjacency(params.dataId);
});

// 2. 双击节点查看详情
chart.on('dblclick', (params) => {
    showDetailModal(params.dataId);
});

// 3. 筛选器：按行业/情感筛选
filterByIndustry('科技');
filterBySentiment('positive');

// 4. 时间滑块：查看历史快照
timeSlider.on('change', (day) => {
    loadGraphSnapshot(day);
});
```

---

### 🟢 P2 - 高级功能

#### 7. 图谱分析指标

**新增指标**:
```python
# 中心性分析
centrality = {
    'degree': nx.degree_centrality(graph),      # 度中心性
    'betweenness': nx.betweenness_centrality(graph),  # 介数中心性
    'pagerank': nx.pagerank(graph)  # PageRank
}

# 找出最关键节点
most_influential = max(centrality['pagerank'], 
                       key=centrality['pagerank'].get)
```

**应用场景**:
- 找出最具影响力的股票
- 识别新闻传播路径
- 发现市场热点

---

#### 8. 相似新闻推荐

**基于向量相似度**:
```python
from sklearn.metrics.pairwise import cosine_similarity

def find_similar_news(news_id, limit=5):
    """查找相似新闻"""
    # 获取新闻向量
    # 计算余弦相似度
    # 返回最相似的 N 条新闻
```

**前端展示**:
- 点击新闻节点
- 侧边栏显示相似新闻
- 形成新闻簇

---

#### 9. 异常检测

**检测模式**:
```python
# 1. 情感突变
if sentiment_change > 0.5 in 1 day:
    alert("情感异常波动")

# 2. 提及暴增
if mention_count > avg * 3:
    alert("关注度异常")

# 3. 社群结构突变
if community_structure_changed > 30%:
    alert("关联关系变化")
```

---

## 📈 优化效果对比

### 当前 vs 优化后

| 指标 | 当前 | 优化后 | 提升 |
|------|------|--------|------|
| **节点数** | 81 | 90-100 | +15% |
| **边数** | 49 | 100-150 | +200% |
| **边类型** | 1 | 4-5 | +400% |
| **社群数** | 0 | 3-5 | ∞ |
| **行业维度** | 无 | 4 个 | 新增 |
| **交互功能** | 基础 | 丰富 | 大幅增强 |

---

## 🛠️ 实施计划

### 第一阶段（1-2 天）
- [ ] 添加共现关系边
- [ ] 添加行业节点
- [ ] 优化节点大小和颜色

### 第二阶段（2-3 天）
- [ ] 增强社群检测
- [ ] 添加时间维度
- [ ] 前端交互优化

### 第三阶段（3-5 天）
- [ ] 图谱分析指标
- [ ] 相似新闻推荐
- [ ] 异常检测告警

---

## 💡 快速优化（30 分钟见效）

### 立即可做的优化

**1. 修改节点大小公式** (文件：`knowledge_graph.py`)
```python
# 当前
size = 20 + abs(data.get('change_percent', 0)) * 2

# 优化后
mention_count = self._count_mentions(symbol)  # 新增方法
size = 15 + mention_count * 3 + abs(change_percent) * 2
# 范围：15 - 60，差异更明显
```

**2. 添加行业分类** (新增配置文件)
```python
# industry_mapping.py
INDUSTRY_MAP = {
    '科技': ['AAPL', 'GOOGL', 'MSFT', 'META', 'NVDA', 'AMD'],
    '加密货币': ['BTC-USD', 'ETH-USD'],
    '汽车': ['TSLA'],
    '电商': ['AMZN']
}
```

**3. 前端颜色区分** (文件：`index.html`)
```javascript
// 按行业设置颜色
const industryColors = {
    '科技': '#8b5cf6',
    '加密货币': '#f59e0b',
    '汽车': '#ef4444',
    '电商': '#10b981'
};
```

---

## 🎯 推荐优先级

### 立即做（今天）
1. ✅ **优化节点大小** - 视觉效果更明显
2. ✅ **添加行业分类** - 结构更清晰

### 本周完成
3. 🔲 **添加共现关系** - 丰富图谱连接
4. 🔲 **增强社群检测** - 发现股票群体
5. 🔲 **前端交互优化** - 用户体验提升

### 下周完成
6. 🔲 **时间维度分析** - 趋势可视化
7. 🔲 **图谱分析指标** - 深度分析
8. 🔲 **异常检测** - 主动告警

---

## 📊 总结

**当前评分**: 70/100

**优点**:
- ✅ 基础功能正常
- ✅ 数据持续更新
- ✅ 前端可视化可用

**待优化**:
- ⚠️ 关系类型单一
- ⚠️ 缺少行业维度
- ⚠️ 交互功能简单
- ⚠️ 视觉效果平淡

**优化后预期**: 90/100

---

需要我帮你实现哪个优化？建议从**节点大小优化**和**行业分类**开始，30 分钟见效！🚀
