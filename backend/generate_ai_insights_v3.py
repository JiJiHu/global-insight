#!/usr/bin/env python3
"""
AI 洞察生成脚本 v3 - 使用 DashScope Qwen3.5-Plus
- 接入真正的 AI 模型进行市场分析
- 基于市场数据和新闻生成深度洞察
- 模型：dashscope-cp/qwen3.5-plus
"""

from datetime import datetime, timedelta
import random
from db import get_db_connection
import json
import os
import requests

# DashScope API 配置
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
# 使用 dashscope 主端点（不是 coding 端点）
DASHSCOPE_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
MODEL = 'qwen-plus'  # 使用 qwen-plus 模型

def call_qwen_api(prompt, system_prompt="你是一个专业的金融分析师。"):
    """调用 Qwen API 生成分析内容"""
    if not DASHSCOPE_API_KEY:
        print("❌ 未配置 DASHSCOPE_API_KEY 环境变量")
        return None
    
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7,
        'max_tokens': 1000
    }
    
    try:
        response = requests.post(DASHSCOPE_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return content
        else:
            print(f"❌ API 返回异常：{result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API 请求失败：{e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败：{e}")
        return None

def cleanup_old_insights(days=7):
    """清理 N 天前的旧洞察，避免标题重复"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        cur.execute("DELETE FROM insights WHERE created_at < %s", (cutoff_date,))
        deleted = cur.rowcount
        conn.commit()
        if deleted > 0:
            print(f"🧹 已清理 {deleted} 条{days}天前的旧洞察")
        cur.close()

def generate_ai_market_insight():
    """使用 AI 生成市场洞察"""
    # 先清理旧数据
    cleanup_old_insights(days=7)
    
    insights = []
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取市场数据
        cur.execute("""
            SELECT DISTINCT ON (symbol) symbol, price, change_percent, type, timestamp
            FROM market_data
            ORDER BY symbol, timestamp DESC
            LIMIT 20
        """)
        market_data = cur.fetchall()
        
        # 获取最新新闻
        cur.execute("""
            SELECT title, source, sentiment_label, created_at
            FROM news
            ORDER BY created_at DESC
            LIMIT 10
        """)
        news_data = cur.fetchall()
        
        cur.close()
    
    # 构建市场数据文本
    market_text = "\n".join([
        f"- {row[0]} ({row[3]}): ${row[1]:.2f}, {row[2]:+.2f}%"
        for row in market_data
    ])
    
    # 构建新闻文本
    news_text = "\n".join([
        f"- [{row[2]}] {row[0]} (来源：{row[1]})"
        for row in news_data
    ])
    
    # 构建 AI 分析提示词
    prompt = f"""
请基于以下市场数据和新闻，生成一份专业的投资洞察分析报告：

## 市场数据
{market_text}

## 最新新闻
{news_text}

请分析：
1. **市场整体趋势**（1-2 句话）
2. **主要风险点**（1-2 个）
3. **潜在投资机会**（1-2 个）
4. **投资建议**（简短明确）

要求：
- 用中文回答
- 专业但易懂
- 给出具体数据支撑
- 避免模糊表述
"""
    
    print(f"\n🧠 正在调用 Qwen3.5-Plus 生成分析...")
    ai_analysis = call_qwen_api(prompt)
    
    if ai_analysis:
        # 提取关键信息生成洞察
        insight = {
            'title': f'🤖 AI 深度分析：{datetime.now().strftime("%m-%d")}',
            'content': ai_analysis,
            'confidence_score': 0.85,
            'analysis_type': 'ai_deep_analysis',
            'created_at': datetime.now()
        }
        insights.append(insight)
        print(f"✅ AI 分析生成成功")
    else:
        print(f"❌ AI 分析生成失败")
    
    return insights

def generate_ai_news_summary():
    """使用 AI 生成新闻摘要"""
    insights = []
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 获取最近的新闻
        cur.execute("""
            SELECT title, content, source, sentiment_label
            FROM news
            WHERE created_at > NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC
            LIMIT 15
        """)
        news_items = cur.fetchall()
        
        cur.close()
    
    if not news_items:
        return insights
    
    # 构建新闻文本
    news_text = "\n\n".join([
        f"标题：{row[0]}\n内容：{row[1][:200]}...\n来源：{row[2]}\n情感：{row[3]}"
        for row in news_items
    ])
    
    prompt = f"""
请总结以下 24 小时内的财经新闻，提炼出最重要的 3 个要点：

{news_text}

请输出：
1. **今日焦点**（最重要的新闻事件）
2. **市场影响**（对股市/ crypto/ 大宗商品的影响）
3. **明日展望**（需要关注的事件）

要求：
- 用中文
- 简洁明了
- 突出关键信息
"""
    
    print(f"\n🧠 正在调用 Qwen3.5-Plus 生成新闻摘要...")
    ai_summary = call_qwen_api(prompt, "你是一个专业的财经新闻编辑。")
    
    if ai_summary:
        insight = {
            'title': f'📰 AI 新闻摘要：{datetime.now().strftime("%m-%d")}',
            'content': ai_summary,
            'confidence_score': 0.80,
            'analysis_type': 'ai_news_summary',
            'created_at': datetime.now()
        }
        insights.append(insight)
        print(f"✅ 新闻摘要生成成功")
    
    return insights

def save_insights(insights):
    """保存洞察到数据库"""
    if not insights:
        return
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        for insight in insights:
            try:
                cur.execute("""
                    INSERT INTO insights (
                        title, content, confidence_score, 
                        analysis_type, created_at
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    insight['title'],
                    insight['content'],
                    insight['confidence_score'],
                    insight['analysis_type'],
                    insight['created_at']
                ))
                print(f"   ✅ 已保存：{insight['title'][:50]}...")
            except Exception as e:
                print(f"   ❌ 保存失败：{e}")
        
        conn.commit()
        cur.close()

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 AI 洞察生成器 v3 (Qwen3.5-Plus)")
    print("=" * 60)
    print(f"\n📅 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M (ID:{id}):%S')}")
    print(f"🔑 API Key: {'已配置' if DASHSCOPE_API_KEY else '❌ 未配置'}")
    print(f"🧠 模型：{MODEL}")
    print("=" * 60)
    
    if not DASHSCOPE_API_KEY:
        print("\n❌ 错误：未配置 DASHSCOPE_API_KEY 环境变量")
        print("\n请在 docker-compose.yml 中添加:")
        print("  environment:")
        print("    - DASHSCOPE_API_KEY=your-api-key")
        return
    
    all_insights = []
    
    # 生成市场洞察
    market_insights = generate_ai_market_insight()
    all_insights.extend(market_insights)
    
    # 生成新闻摘要
    news_insights = generate_ai_news_summary()
    all_insights.extend(news_insights)
    
    # 保存到数据库
    print(f"\n💾 保存洞察到数据库...")
    save_insights(all_insights)
    
    print(f"\n✅ 完成！共生成了 {len(all_insights)} 条 AI 洞察")
    print("=" * 60)

if __name__ == "__main__":
    main()
