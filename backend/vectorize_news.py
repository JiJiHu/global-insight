#!/usr/bin/env python3
"""
新闻向量化管道
- 加载中文文本嵌入模型
- 将新闻文本转换为向量
- 存入 PostgreSQL
"""
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from config import EMBEDDING_MODEL, SENTIMENT_MODEL, EMBEDDING_DIM
from db import insert_news, get_db_connection
import numpy as np

class NewsVectorizer:
    def __init__(self):
        print("🧠 加载模型中...")
        
        # 加载向量化模型
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✅ 向量模型已加载：{EMBEDDING_MODEL}")
        
        # 加载情感分析模型
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=SENTIMENT_MODEL,
            device=-1  # CPU
        )
        print(f"✅ 情感模型已加载：{SENTIMENT_MODEL}")
    
    def generate_embedding(self, text):
        """生成文本向量"""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32).tolist()
    
    def analyze_sentiment(self, text):
        """情感分析"""
        try:
            result = self.sentiment_pipeline(text[:512])[0]  # 限制长度
            label = result['label']
            score = float(result['score'])
            
            # 转换为 -1 到 1 的分数
            # 1-5 星 → -1 到 1
            stars = int(label[0])
            sentiment_score = (stars - 3) / 2.0  # -1, -0.5, 0, 0.5, 1
            
            sentiment_label = 'positive' if stars >= 4 else ('negative' if stars <= 2 else 'neutral')
            
            return sentiment_score, sentiment_label
        except Exception as e:
            print(f"⚠️ 情感分析失败：{e}")
            return 0.0, 'neutral'
    
    def extract_symbols(self, text):
        """从文本中提取相关金融标的 (简单规则)"""
        symbols = []
        
        # 美股
        us_stocks = ["AAPL", "TSLA", "NVDA", "GOOGL", "MSFT", "AMD", "META", "AMZN"]
        for symbol in us_stocks:
            if symbol in text.upper():
                symbols.append(symbol)
        
        # A 股简称
        if "茅台" in text or "贵州茅台" in text:
            symbols.append("600519.SS")
        if "宁德" in text or "宁德时代" in text:
            symbols.append("300750.SZ")
        
        # 商品
        if "黄金" in text or "gold" in text.lower():
            symbols.append("GOLD")
        if "石油" in text or "原油" in text.lower():
            symbols.append("WTI")
        if "比特币" in text or "BTC" in text or "bitcoin" in text.lower():
            symbols.append("BTC-USD")
        if "以太坊" in text or "ETH" in text or "ethereum" in text.lower():
            symbols.append("ETH-USD")
        
        return symbols if symbols else None
    
    def process_news(self, title, content, source, url=None):
        """处理单条新闻"""
        print(f"\n📰 处理：{title[:50]}...")
        
        # 生成向量
        full_text = f"{title} {content}" if content else title
        embedding = self.generate_embedding(full_text)
        print(f"   ✅ 向量生成：{len(embedding)}维")
        
        # 情感分析
        sentiment_score, sentiment_label = self.analyze_sentiment(full_text)
        print(f"   ✅ 情感：{sentiment_label} ({sentiment_score:.2f})")
        
        # 提取相关标的
        related_symbols = self.extract_symbols(full_text)
        if related_symbols:
            print(f"   ✅ 相关标的：{related_symbols}")
        
        # 存入数据库
        insert_news(
            title=title,
            content=content,
            source=source,
            url=url,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            embedding=embedding,
            related_symbols=related_symbols
        )
        print(f"   ✅ 已存入数据库")
    
    def process_batch(self, news_list):
        """批量处理新闻"""
        print(f"\n🚀 开始批量处理 {len(news_list)} 条新闻...")
        for i, news in enumerate(news_list, 1):
            print(f"\n[{i}/{len(news_list)}]")
            self.process_news(**news)

# 测试数据
TEST_NEWS = [
    {
        "title": "特斯拉发布新车型，股价大涨 5%",
        "content": "特斯拉公司今日发布了全新 Model 2 车型，定价 2.5 万美元，市场反应热烈。分析师认为这将进一步推动特斯拉在电动车市场的份额。",
        "source": "twitter",
        "url": "https://twitter.com/tesla/status/xxx"
    },
    {
        "title": "黄金价格突破 2000 美元大关",
        "content": "受地缘政治紧张局势影响，国际黄金价格今日突破 2000 美元/盎司，创下历史新高。投资者纷纷转向避险资产。",
        "source": "cctv",
        "url": "https://news.cctv.com/xxx"
    },
    {
        "title": "贵州茅台发布年报，净利润增长 15%",
        "content": "贵州茅台今日发布 2024 年年报，实现营业收入 1500 亿元，同比增长 18%，净利润增长 15%。机构维持买入评级。",
        "source": "wechat",
        "url": "https://mp.weixin.qq.com/s/xxx"
    },
    {
        "title": "比特币跌破 6 万美元，市场恐慌",
        "content": "比特币今日大幅下跌，跌破 6 万美元关口，24 小时跌幅超过 8%。分析师认为这与美联储加息预期有关。",
        "source": "twitter",
        "url": "https://twitter.com/xxx"
    },
]

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 新闻向量化管道测试")
    print("=" * 60)
    
    vectorizer = NewsVectorizer()
    vectorizer.process_batch(TEST_NEWS)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)
