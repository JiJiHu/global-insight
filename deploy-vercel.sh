#!/bin/bash
# Global Insight Vercel 部署脚本
set -e

echo "🚀 部署到 Vercel..."

cd /root/global-insight

# 1. 确保所有更改已提交
echo "📝 检查 Git 状态..."
git add -A
git diff --cached --quiet || git commit -m "chore: auto-deploy $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# 2. 触发 Vercel 部署
echo "📦 触发 Vercel 部署..."
vercel pull --yes
vercel --prod

echo "✅ 部署完成！"
echo "🌐 访问：https://global-insight-production.up.railway.app"
