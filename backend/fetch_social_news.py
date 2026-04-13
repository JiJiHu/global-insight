#!/usr/bin/env python3
"""
社交媒体新闻抓取脚本
- Twitter/X (通过 agent-reach)
- 微信公众号 (通过 x-reader)
"""
import sys
import subprocess
from datetime import datetime
sys.path.insert(0, '/root/finance-dashboard/backend')

from vectorize_news import NewsVectorizer
from db import insert_news

# 财经相关的 Twitter 账号和微信公众号
TWITTER_ACCOUNTS = [
    "elonmusk",      # Tesla, SpaceX
    "OpenAI",        # AI news
    "nvidia",        # GPU, AI chips
    "WSJ",           # Wall Street Journal
    "Reuters",       # 路透社
]

WECHAT_ACCOUNTS = [
    "华尔街见闻",     # 财经新闻
    "券商中国",       # 证券新闻
    "财新",          # 财经媒体
]

def fetch_twitter_news():
    """抓取 Twitter 财经新闻"""
    print("\n🐦 抓取 Twitter 新闻...")
    news_list = []
    
    for account in TWITTER_ACCOUNTS[:3]:  # 限制 3 个账号
        try:
            # 使用 x-reader 技能
            # 注意：实际需要通过 OpenClaw 调用
            print(f"   ⏳ @{account}...")
            
            # 模拟数据（实际应调用 x-reader）
            # 真实调用：node /root/.openclaw/skills/x-reader/index.js --url https://twitter.com/{account}
            
        except Exception as e:
            print(f"   ❌ @{account} 失败：{e}")
    
    return news_list

def fetch_wechat_news():
    """抓取微信公众号文章"""
    print("\n💬 抓取微信新闻...")
    news_list = []
    
    # 示例：最近分享的公众号文章
    wechat_urls = [
        # 这些是示例 URL，实际应从 RSS 或订阅列表获取
        # "https://mp.weixin.qq.com/s/xxxxx"
    ]
    
    for url in wechat_urls:
        try:
            # 使用 x-reader 技能
            result = subprocess.run(
                ["node", "/root/.openclaw/skills/x-reader/index.js", "--url", url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析返回的文章内容
                print(f"   ✅ {url}")
                # TODO: 解析并添加到 news_list
                
        except Exception as e:
            print(f"   ❌ {url} 失败：{e}")
    
    return news_list

def fetch_manual_finance_news():
    """手动添加一些财经新闻（演示用）"""
    print("\n📰 添加财经新闻...")
    
    news_list = [
        {
            "title": "苹果发布新一代 iPhone，股价创新高",
            "content": "苹果公司今日发布了 iPhone 16 系列，搭载 A18 芯片和 AI 功能。分析师认为这将推动换机潮，目标价上调至 300 美元。",
            "source": "twitter-AAPL",
            "url": "https://twitter.com/Apple/status/xxx"
        },
        {
            "title": "特斯拉上海工厂产能突破 100 万辆",
            "content": "特斯拉上海超级工厂年度产能突破 100 万辆，成为中国最大的新能源汽车出口基地。马斯克表示将继续扩大投资。",
            "source": "wechat-特斯拉",
            "url": "https://mp.weixin.qq.com/s/xxx"
        },
        {
            "title": "英伟达 H200 芯片供不应求",
            "content": "英伟达最新 AI 芯片 H200 订单排到 2026 年底，微软、谷歌、Meta 争相采购。分析师维持买入评级。",
            "source": "twitter-NVDA",
            "url": "https://twitter.com/nvidia/status/xxx"
        },
        {
            "title": "美联储维持利率不变",
            "content": "美联储 FOMC 会议决定维持基准利率不变，符合市场预期。鲍威尔表示通胀正在缓解，但不急于降息。",
            "source": "twitter-Fed",
            "url": "https://twitter.com/FederalReserve/status/xxx"
        },
        {
            "title": "比亚迪超越特斯拉成全球电动车销冠",
            "content": "比亚迪 2025 年 Q4 销量超越特斯拉，成为全球最大的纯电动车制造商。王朝系列和海洋系列持续热销。",
            "source": "wechat-比亚迪",
            "url": "https://mp.weixin.qq.com/s/xxx"
        },
    ]
    
    print(f"   ✅ 准备 {len(news_list)} 条财经新闻")
    return news_list

def process_news(news_list):
    """处理新闻并向量化"""
    if not news_list:
        print("⚠️ 没有新闻需要处理")
        return
    
    print(f"\n🧠 开始向量化 {len(news_list)} 条新闻...")
    vectorizer = NewsVectorizer()
    
    success = 0
    for i, news in enumerate(news_list, 1):
        try:
            print(f"\n[{i}/{len(news_list)}] {news['title'][:50]}...")
            vectorizer.process_news(**news)
            success += 1
        except Exception as e:
            print(f"❌ 处理失败：{e}")
    
    print(f"\n✅ 完成！成功：{success}/{len(news_list)}")

def fetch_and_vectorize_news():
    """主函数"""
    print(f"\n📱 开始抓取社交媒体新闻 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 抓取 Twitter
    twitter_news = fetch_twitter_news()
    
    # 抓取微信
    wechat_news = fetch_wechat_news()
    
    # 添加财经新闻（演示）
    finance_news = fetch_manual_finance_news()
    
    # 合并所有新闻
    all_news = twitter_news + wechat_news + finance_news
    
    # 处理并向量化
    process_news(all_news)
    
    print("\n" + "=" * 60)
    print("✅ 社交媒体新闻抓取完成!")

if __name__ == "__main__":
    fetch_and_vectorize_news()
