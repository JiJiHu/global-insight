#!/bin/bash
# 安装依赖脚本

set -e

echo "🚀 开始安装 Finance Dashboard 后端依赖..."
echo "=" * 60

cd /root/finance-dashboard/backend

# 创建虚拟环境
echo "📦 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📦 安装 Python 依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=" * 60
echo "✅ 安装完成!"
echo ""
echo "使用方法:"
echo "  source venv/bin/activate"
echo "  python fetch_market_data.py    # 抓取金融数据"
echo "  python vectorize_news.py       # 测试向量化"
echo "  python api.py                  # 启动 API 服务"
echo "  python run_pipeline.py         # 运行完整管道"
echo "=" * 60
