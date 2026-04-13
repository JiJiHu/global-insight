# Vercel 专用配置
import os

# 从 Vercel 环境变量读取
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("POSTGRES_PRISMA_URL")

# 如果没有环境变量，使用默认值
if not DATABASE_URL:
    DATABASE_URL = "postgresql://jack:ChangeMe123!@localhost:5432/finance_insight"

# Finnhub API Key
FINNHUB_API_KEY = "d6l40k1r01qptf3ons10d6l40k1r01qptf3ons1g"

# 监控的金融标的
WATCHLIST = {
    "stocks_us": ["AAPL", "TSLA", "NVDA", "GOOGL", "MSFT", "AMD", "META", "AMZN"],
    "stocks_cn": ["600519.SS", "300750.SZ"],
    "crypto": ["BTCUSD", "ETHUSD"],
    "forex": ["EUR", "GBP", "JPY", "CNY"]
}

# 向量化模型（Vercel 不使用）
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
EMBEDDING_DIM = 768

# 情感分析模型（Vercel 不使用）
SENTIMENT_MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"
