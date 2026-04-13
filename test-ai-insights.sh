#!/bin/bash
# 测试 DashScope AI 洞察生成

echo "🧪 测试 DashScope AI 洞察生成"
echo "======================================"
echo ""

# 检查环境变量
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "❌ 未设置 DASHSCOPE_API_KEY 环境变量"
    echo ""
    echo "💡 请先配置 API Key:"
    echo "   bash /root/global-insight/config-dashscope.sh"
    exit 1
fi

echo "✅ API Key 已配置"
echo ""

# 运行 AI 洞察生成脚本
echo "🚀 运行 AI 洞察生成..."
docker exec global-insight-backend python3 generate_ai_insights_v3.py

echo ""
echo "📊 查看最新 AI 洞察:"
docker exec global-insight-backend curl -s "http://localhost:8000/api/v1/insights?limit=3" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, insight in enumerate(data, 1):
    print(f'\n{i}. {insight[\"title\"]}')
    print(f'   来源：{insight.get(\"source\", \"未知\")}')
    print(f'   类型：{insight.get(\"analysis_type\", \"未知\")}')
    print(f'   置信度：{insight.get(\"confidence_score\", 0)*100:.0f}%')
"

echo ""
echo "======================================"
echo "✅ 测试完成！"
