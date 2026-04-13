# Global Insight 优化计划

## 🎯 优化目标
将"金融大数据看板"升级为"一起看世界 | Global Insight"国际化视野平台

---

## 📋 优化清单

### 1. 主页美化 ✅ 优先级：高
**现状**：简单的紫色渐变背景
**目标**：
- 标题改为"一起看世界 | Global Insight"
- 添加地球/世界地图相关配图或背景
- 优化整体视觉风格（国际化、专业感）
- 添加副标题："洞察全球市场 · 把握投资机遇"

**实现方案**：
- 使用高质量的地球/世界地图背景图（Unsplash 免费图库）
- 优化 header 设计，增加视觉层次
- 添加动态效果（如地球旋转动画或粒子效果）

---

### 2. 数据完整性 ✅ 优先级：高
**问题**：
- 黄金和石油数据为空
- 加密货币数据过时

**实现方案**：
- 添加黄金数据源（伦敦金银市场 LBMA API 或 金投网）
- 添加石油数据源（Brent/WTI 原油期货 API）
- 更新加密货币数据源（CoinGecko API 或 Binance API）
- 设置定时刷新（每 5-10 分钟）

**数据源**：
```python
# 黄金
https://www.goldapi.io/
https://api.gold-api.com/

# 石油
https://www.alphavantage.co/
https://polygon.io/

# 加密货币
https://api.coingecko.com/api/v3
https://api.binance.com/api/v3
```

---

### 3. AI 洞察增强 ✅ 优先级：高
**问题**：
- 文章数量太少（仅 5 条）
- 内容重复
- 数据源单一
- 无法点击查看详细文章

**实现方案**：
- 增加数据源：Twitter API、Reddit、Seeking Alpha、Bloomberg、Reuters
- 使用 x-reader 技能解析社交媒体内容
- 添加文章详情页面（或弹窗显示完整内容）
- 增加去重逻辑（基于标题相似度）
- 生成更多维度的洞察（行业分析、趋势预测、风险评估）

**新增 API**：
```
GET /api/v1/insights/detail?id=xxx  # 获取洞察详情
GET /api/v1/insights/sources         # 获取数据源列表
```

---

### 4. 知识图谱完善 ✅ 优先级：中
**问题**：
- 只有节点没有边（25 个节点，0 条边）
- 无法看到关联性

**实现方案**：
- 定义实体关系类型：
  - 公司 → 行业（belongs_to）
  - 公司 → 竞争对手（competes_with）
  - 公司 → 合作伙伴（partners_with）
  - 新闻 → 涉及公司（mentions）
  - 人物 → 任职公司（works_for）
- 从新闻内容中提取关系（NLP 实体识别）
- 使用行业映射表建立公司与行业的关系
- 可视化优化：不同关系类型用不同颜色/线型

**新增 API**：
```
GET /api/v1/graph/full  # 获取完整图谱（含边）
GET /api/v1/graph/relations?symbol=xxx  # 获取某公司的关联关系
```

---

### 5. 新闻源扩展 ✅ 优先级：高
**问题**：
- 只显示 finnhub 源
- 缺少 Twitter、主流网站

**实现方案**：
- 集成 Twitter API（使用 agent-reach 技能）
- 添加 RSS 订阅源（主流财经媒体）
- 使用 x-reader 解析微信公众号、小红书等内容
- 新闻列表增加"来源"图标/标识
- 支持按来源筛选

**新增数据源**：
- Twitter/X（财经大 V、官方账号）
- 微信公众号（财经类）
- 主流财经媒体 RSS（CNBC、Bloomberg、Reuters、财新、华尔街见闻）
- Reddit（r/wallstreetbets、r/investing）

**前端优化**：
- 新闻卡片显示来源图标
- 点击标题直接打开原文（新标签页）
- 支持按来源/情感/时间筛选

---

### 6. Dashboard 统计优化 ✅ 优先级：中
**问题**：
- 只显示数据量，无法查看详细数据

**实现方案**：
- 统计卡片改为可点击
- 点击后弹出详细数据表格
- 或跳转到独立的数据浏览页面

**交互设计**：
```
统计卡片（如"新闻 1,650 条"）
    ↓ 点击
数据浏览弹窗/页面
    - 列表展示
    - 支持搜索/筛选/分页
    - 可导出 CSV
```

---

## 🚀 实施计划

### Phase 1: 核心功能优化（1-2 天）
1. 主页美化（前端）
2. 黄金/石油/加密货币数据接入（后端）
3. 新闻源扩展（后端 + 前端）

### Phase 2: 数据增强（2-3 天）
4. AI 洞察增强（后端 NLP + 前端展示）
5. 知识图谱关系构建（后端 + 可视化）

### Phase 3: 交互优化（1 天）
6. Dashboard 数据浏览功能（前端）

---

## 📊 技术栈

**前端**：
- Vue 3.4.19
- Element Plus
- ECharts 5.4.3
- Axios

**后端**：
- FastAPI
- PostgreSQL + pgvector
- Python 3.11

**数据源**：
- Finnhub（股票）
- CoinGecko（加密货币）
- GoldAPI（黄金）
- AlphaVantage（石油）
- Twitter API / x-reader（社交媒体）
- RSS feeds（新闻媒体）

---

## ✅ 验收标准

1. [ ] 主页显示"一起看世界 | Global Insight"标题和地球相关配图
2. [ ] 黄金、石油、加密货币数据实时更新
3. [ ] AI 洞察显示至少 20 条不重复内容，可点击查看详情
4. [ ] 知识图谱显示节点间的关联关系（至少 50 条边）
5. [ ] 新闻列表显示多个来源（finnhub、Twitter、Reuters 等）
6. [ ] 点击统计卡片可查看/导出详细数据

---

*Created: 2026-03-11*
*Project: Global Insight (一起看世界)*
