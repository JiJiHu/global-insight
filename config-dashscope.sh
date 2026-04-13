#!/bin/bash
# 配置 DashScope API Key

echo "🔑 配置 DashScope API Key"
echo "======================================"
echo ""

# 检查是否提供了 API Key
if [ -n "$1" ]; then
    API_KEY="$1"
else
    echo "💡 请从以下地址获取 API Key:"
    echo "   https://dashscope.console.aliyun.com/"
    echo ""
    read -p "输入您的 DashScope API Key: " -r API_KEY
    echo ""
fi

if [ -z "$API_KEY" ]; then
    echo "❌ API Key 不能为空"
    exit 1
fi

# 1. 设置环境变量
echo "1️⃣  设置环境变量..."
export DASHSCOPE_API_KEY="$API_KEY"
echo "   ✅ 当前会话环境变量已设置"

# 2. 添加到 ~/.bashrc 永久生效
if ! grep -q "DASHSCOPE_API_KEY" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# DashScope API Key" >> ~/.bashrc
    echo "export DASHSCOPE_API_KEY=\"$API_KEY\"" >> ~/.bashrc
    echo "   ✅ 已添加到 ~/.bashrc (永久生效)"
else
    sed -i "/^export DASHSCOPE_API_KEY=/d" ~/.bashrc
    echo "export DASHSCOPE_API_KEY=\"$API_KEY\"" >> ~/.bashrc
    echo "   ✅ 已更新 ~/.bashrc"
fi

# 3. 更新 docker-compose.yml 并重启
echo ""
echo "2️⃣  重启 Docker 服务..."
cd /root/global-insight

# 导出环境变量供 docker-compose 使用
export DASHSCOPE_API_KEY="$API_KEY"

# 重启 backend 服务
docker-compose up -d --force-recreate backend

echo ""
echo "3️⃣  验证配置..."
sleep 5

# 测试 API Key 是否生效
docker exec global-insight-backend bash -c "if [ -n \"\$DASHSCOPE_API_KEY\" ]; then echo '✅ API Key 已配置'; else echo '❌ API Key 未配置'; fi"

echo ""
echo "4️⃣  测试 AI 洞察生成..."
docker exec global-insight-backend python3 generate_ai_insights_v3.py

echo ""
echo "======================================"
echo "✅ 配置完成！"
echo ""
echo "💡 下次使用时，API Key 会自动加载"
echo "   如需修改，重新运行此脚本即可"
echo ""
echo "📝 手动运行 AI 洞察生成:"
echo "   docker exec global-insight-backend python3 generate_ai_insights_v3.py"
echo ""
