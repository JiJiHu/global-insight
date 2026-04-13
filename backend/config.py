# 数据库配置
import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jack:ChangeMe123!@localhost:5432/finance_insight")

# Finnhub API Key (60 次/分钟 = 86,400 次/天)
FINNHUB_API_KEY = "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"

# 监控的金融标的
WATCHLIST = {
    "stocks_us": ["AAPL", "TSLA", "NVDA", "GOOGL", "MSFT", "AMD", "META", "AMZN"],
    "stocks_cn": ["600519.SS", "300750.SZ"],  # 茅台、宁德
    "crypto": ["BTCUSD", "ETHUSD"],
    "forex": ["EUR", "GBP", "JPY", "CNY"]
}

# 向量化模型
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
EMBEDDING_DIM = 768

# 情感分析模型
SENTIMENT_MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"
