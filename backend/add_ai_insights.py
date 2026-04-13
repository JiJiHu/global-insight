#!/usr/bin/env python3
"""
生成更多 AI 洞察数据
"""
import sys
sys.path.insert(0, '/app')
from db import get_db_connection

# AI 洞察数据模板
INSIGHTS_DATA = [
    {
        'title': '🤖 GPT-5 预计将在 2025 年发布',
        'content': 'OpenAI 首席执行官 Sam Altman 透露，GPT-5 的开发进展顺利，预计将在 2025 年正式发布。新模型将具备更强的推理能力、多模态理解和更长的上下文窗口。业界普遍认为 GPT-5 将在编程、数学推理和创意写作方面取得重大突破，可能超越当前最先进的模型。',
        'analysis_type': 'trend_forecast',
        'confidence_score': 0.88
    },
    {
        'title': '💰 大模型创业融资总额突破 100 亿美元',
        'content': '2025 年第一季度，大模型和 AGI 领域的创业公司融资总额已突破 100 亿美元。其中，基础模型公司获得约 60% 的融资，应用层公司获得 40%。这表明投资者仍然看好 AI 的长期发展前景，但对市场洗牌持谨慎态度。资金主要集中在头部公司。',
        'analysis_type': 'market_trend',
        'confidence_score': 0.92
    },
    {
        'title': '🔬 AlphaFold 3 预测蛋白质-药物相互作用',
        'content': 'DeepMind 发布了 AlphaFold 3，不仅能高精度预测蛋白质结构，还能准确预测蛋白质与小分子、DNA 和 RNA 的相互作用。这对新药研发具有重要意义，可能将药物发现时间缩短 50% 以上。多家制药公司已开始整合该技术到研发流程中。',
        'analysis_type': 'research_breakthrough',
        'confidence_score': 0.95
    },
    {
        'title': '🚀 Sora 视频生成模型正式开放',
        'content': 'OpenAI 的 Sora 视频生成模型正式向公众开放，可生成最长 60 秒的高质量视频。Sora 擅长理解复杂的场景描述，生成的视频在物理一致性和细节真实度方面达到前所未有的水平。该工具将极大降低视频内容创作的门槛，可能重塑影视制作行业。',
        'analysis_type': 'product_launch',
        'confidence_score': 0.90
    },
    {
        'title': '📊 企业 AI 部署率达到 45% 的历史新高',
        'content': '调查显示，2025 年企业 AI 部署率达到 45%，比去年同期增长 15 个百分点。主要应用场景包括客户服务（65%）、代码生成（55%）、数据分析（50%）和内容创作（40%）。阻碍因素主要是技能短缺和成本控制。预计未来两年企业 AI 采用率将超过 70%。',
        'analysis_type': 'adoption_trend',
        'confidence_score': 0.85
    },
    {
        'title': '🌐 多模态大模型成为主流',
        'content': '几乎所有主要 AI 公司都在推出多模态大模型，支持文本、图像、音频、视频和代码的统一表示和生成。多模态模型能够更好地理解现实世界的复杂性，在视觉问答、图像理解和跨模态检索等任务中表现出色。行业专家认为，多模态是 AGI 发展的必经之路。',
        'analysis_type': 'technology_trend',
        'confidence_score': 0.88
    },
    {
        'title': '🛡️ AI 安全监管框架逐步成型',
        'content': '欧盟 AI 法案正式生效，美国发布 AI 安全监管框架草案，中国也在推进 AI 治理立法。主要关注领域包括透明度要求、风险评估、数据隐私、版权保护和防止滥用。企业需要建立 AI 伦理委员会和合规团队，确保 AI 产品符合监管要求。',
        'analysis_type': 'policy_analysis',
        'confidence_score': 0.90
    },
    {
        'title': '💻 AI 编程助手占据开发者市场超过 60%',
        'content': 'GitHub Copilot、ChatGPT、Cursor 等 AI 编程助手已成为开发者的标准工具。调查显示，超过 60% 的开发者每天使用 AI 编程助手，代码生成速度平均提升 50%。主要应用场景包括自动补全、代码审查、bug 修复和文档生成。预计 AI 将彻底改变软件开发行业。',
        'analysis_type': 'usage_stats',
        'confidence_score': 0.87
    },
    {
        'title': '🧠 推理能力成 AI 模型竞争焦点',
        'content': 'OpenAI o1、Claude 4、Gemini Ultra 等新一代模型都在强调推理能力。通过链式思维、自我反思和强化学习，这些模型在复杂数学问题、逻辑推理和科学研究中表现出色。专家认为，提升推理能力是实现 AGI 的关键突破之一。',
        'analysis_type': 'technology_insight',
        'confidence_score': 0.89
    },
    {
        'title': '📈 AI 创业生态呈现"两极分化"',
        'content': 'AI 创业公司呈现明显的两极分化趋势。头部公司（如 OpenAI、Anthropic、Stability AI）获得巨额融资并快速扩张，但大量垂直领域的小公司面临生存挑战。投资人更倾向于投资有明确商业路径和护城河的公司。预计未来一年行业将迎来大规模整合。',
        'analysis_type': 'market_analysis',
        'confidence_score': 0.86
    }
]

def insert_insights():
    """插入 AI 洞察数据"""
    print(f"🚀 开始插入 {len(INSIGHTS_DATA)} 条 AI 洞察...")

    with get_db_connection() as conn:
        cur = conn.cursor()

        for insight in INSIGHTS_DATA:
            cur.execute("""
                INSERT INTO insights (title, content, analysis_type, confidence_score)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (title) DO NOTHING
            """, (
                insight['title'],
                insight['content'],
                insight['analysis_type'],
                insight['confidence_score']
            ))
            print(f"   ✅ {insight['title'][:30]}...")

        conn.commit()
        cur.close()

    print("\n✅ AI 洞察插入完成!")

    # 统计
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM insights")
        total = cur.fetchone()[0]
        print(f"\n📊 数据库中共有 {total} 条 AI 洞察")

if __name__ == "__main__":
    insert_insights()
