#!/usr/bin/env python3
"""
行业分类和主题映射
用于知识图谱的行业维度和主题分析
"""

# 行业分类
INDUSTRY_MAP = {
    '科技': ['AAPL', 'GOOGL', 'MSFT', 'META', 'NVDA', 'AMD', 'INTC', 'CRM'],
    '加密货币': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD'],
    '汽车': ['TSLA', 'F', 'GM', 'RIVN'],
    '电商': ['AMZN', 'BABA', 'JD', 'PDD'],
    '金融': ['JPM', 'BAC', 'GS', 'MS', 'WFC'],
    '能源': ['XOM', 'CVX', 'COP', 'SLB'],
    '医药': ['JNJ', 'PFE', 'MRNA', 'ABBV'],
    '消费': ['WMT', 'COST', 'PG', 'KO', 'PEP']
}

# 反向映射：股票 → 行业
STOCK_TO_INDUSTRY = {}
for industry, stocks in INDUSTRY_MAP.items():
    for stock in stocks:
        STOCK_TO_INDUSTRY[stock] = industry

# 主题关键词映射
THEME_KEYWORDS = {
    # 战争/地缘政治主题
    'war_geopolitics': {
        'keywords': [
            'war', '战争', 'conflict', '冲突', 'military', '军事',
            'invasion', '入侵', 'missile', '导弹', 'attack', '袭击',
            'Iran', '伊朗', 'Israel', '以色列', 'Russia', '俄罗斯',
            'Ukraine', '乌克兰', 'Hezbollah', '真主党', 'Middle East', '中东',
            'tension', '紧张', 'sanction', '制裁'
        ],
        'related_assets': ['GLD', 'GC=F', 'XOM', 'CVX', 'BTC-USD'],  # 黄金、石油、加密货币
        'impact': '避险情绪上升，黄金/石油价格上涨'
    },
    
    # AI 主题
    'ai_tech': {
        'keywords': [
            'AI', '人工智能', 'artificial intelligence', 'machine learning', '机器学习',
            'ChatGPT', 'GPT', 'LLM', '大模型', 'deep learning', '深度学习',
            'NVIDIA', 'GPU', '芯片', 'semiconductor', '半导体',
            'H200', 'A100', 'H100', 'Blackwell', 'Rubin',
            'OpenAI', 'Anthropic', 'Google DeepMind', 'Meta AI',
            'inference', '推理', 'training', '训练', 'compute', '算力'
        ],
        'related_assets': ['NVDA', 'GOOGL', 'MSFT', 'META', 'AMD', 'AAPL'],
        'impact': 'AI 需求增长，芯片股受益'
    },
    
    # 石油/能源主题
    'oil_energy': {
        'keywords': [
            'oil', '石油', 'crude', '原油', 'energy', '能源',
            'OPEC', '欧佩克', 'production', '产量', 'supply', '供应',
            'barrel', '桶', 'refinery', '炼油', 'gasoline', '汽油',
            'Brent', 'WTI', 'pipeline', '管道'
        ],
        'related_assets': ['XOM', 'CVX', 'COP', 'SLB', 'USO'],
        'impact': '油价波动影响能源股'
    },
    
    # 黄金/贵金属主题
    'gold_precious': {
        'keywords': [
            'gold', '黄金', 'precious metal', '贵金属', 'silver', '白银',
            'safe haven', '避险', 'hedge', '对冲', 'inflation', '通胀',
            'Fed', '美联储', 'interest rate', '利率', 'dollar', '美元',
            'GLD', '盎司', 'ounce'
        ],
        'related_assets': ['GLD', 'GC=F', 'SLV', 'NEM', 'GOLD'],
        'impact': '避险或抗通胀需求'
    },
    
    # 美联储/利率主题
    'fed_rate': {
        'keywords': [
            'Fed', '美联储', 'Federal Reserve', 'interest rate', '利率',
            'rate cut', '降息', 'rate hike', '加息', 'Powell', '鲍威尔',
            'inflation', '通胀', 'CPI', 'PCE', 'employment', '就业',
            'quantitative easing', '量化宽松', 'QE', 'QT'
        ],
        'related_assets': ['SPY', 'TLT', 'GLD', 'DXY'],
        'impact': '利率政策影响全市场'
    },
    
    # 电动汽车主题
    'ev_auto': {
        'keywords': [
            'EV', '电动车', 'electric vehicle', 'Tesla', '特斯拉',
            'battery', '电池', 'charging', '充电', 'autonomous', '自动驾驶',
            'FSD', 'Full Self-Driving', 'Cybertruck', 'Model Y', 'Model 3'
        ],
        'related_assets': ['TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV'],
        'impact': '电动车市场竞争加剧'
    }
}

# 反向映射：关键词 → 主题
KEYWORD_TO_THEME = {}
for theme, data in THEME_KEYWORDS.items():
    for keyword in data['keywords']:
        KEYWORD_TO_THEME[keyword.lower()] = theme

def detect_theme(title, content=''):
    """检测新闻主题"""
    text = (title + ' ' + content).lower()
    
    detected_themes = {}
    for theme, data in THEME_KEYWORDS.items():
        score = 0
        for keyword in data['keywords']:
            if keyword.lower() in text:
                score += 1
        
        if score > 0:
            detected_themes[theme] = {
                'score': score,
                'keywords_matched': score,
                'related_assets': data['related_assets'],
                'impact': data['impact']
            }
    
    return detected_themes

def get_industry(stock):
    """获取股票所属行业"""
    return STOCK_TO_INDUSTRY.get(stock, '其他')

def get_theme_assets(theme):
    """获取主题相关资产"""
    if theme in THEME_KEYWORDS:
        return THEME_KEYWORDS[theme]['related_assets']
    return []
